
import logging
import time

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from emails.models import EmailProcessingJob
from processing.pipeline import EmailProcessingPipeline

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Process queued email jobs in the background."

    def add_arguments(self, parser):
        parser.add_argument(
            "--poll-interval",
            type=float,
            default=2.0,
            help="Seconds to wait when no jobs are pending.",
        )
        parser.add_argument(
            "--continuous",
            action="store_true",
            help="Keep running and poll for new jobs.",
        )
        parser.add_argument(
            "--recover-stale-minutes",
            type=int,
            default=0,
            help="Requeue jobs stuck in processing for this many minutes.",
        )

    def handle(self, *args, **options):
        poll_interval = options["poll_interval"]
        continuous = options["continuous"]
        stale_minutes = options["recover_stale_minutes"]

        if poll_interval <= 0:
            self.stderr.write("--poll-interval must be greater than zero.")
            return

        if stale_minutes < 0:
            self.stderr.write(
                "--recover-stale-minutes cannot be negative."
            )
            return

        if stale_minutes:
            cutoff = timezone.now() - timezone.timedelta(
                minutes=stale_minutes
            )
            recovered = EmailProcessingJob.objects.filter(
                status=EmailProcessingJob.Status.PROCESSING,
                started_at__lt=cutoff,
            ).update(
                status=EmailProcessingJob.Status.PENDING,
                started_at=None,
                updated_at=timezone.now(),
            )
            self.stdout.write(
                f"Requeued {recovered} stale job(s)."
            )

        pipeline = EmailProcessingPipeline()

        while True:
            job = self.claim_next_job()

            if job is None:
                if not continuous:
                    self.stdout.write("No pending jobs.")
                    return

                time.sleep(poll_interval)
                continue

            self.stdout.write(f"Processing job {job.pk}...")

            try:
                pipeline.process_file(job.source_path)

                EmailProcessingJob.objects.filter(
                    pk=job.pk,
                    status=EmailProcessingJob.Status.PROCESSING,
                ).update(
                    status=EmailProcessingJob.Status.COMPLETED,
                    completed_at=timezone.now(),
                    error_message="",
                    updated_at=timezone.now(),
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Job {job.pk} completed."
                    )
                )

            except Exception as exc:
                logger.exception("Background job %s failed", job.pk)

                # Avoid storing potentially sensitive exception details.
                error_summary = type(exc).__name__

                EmailProcessingJob.objects.filter(
                    pk=job.pk,
                    status=EmailProcessingJob.Status.PROCESSING,
                ).update(
                    status=EmailProcessingJob.Status.FAILED,
                    error_message=error_summary,
                    updated_at=timezone.now(),
                )

                self.stderr.write(
                    self.style.ERROR(
                        f"Job {job.pk} failed: {error_summary}"
                    )
                )

    def claim_next_job(self):
        with transaction.atomic():
            job = (
                EmailProcessingJob.objects
                .select_for_update()
                .filter(status=EmailProcessingJob.Status.PENDING)
                .order_by("created_at")
                .first()
            )

            if job is None:
                return None

            job.status = EmailProcessingJob.Status.PROCESSING
            job.attempt_count += 1
            job.started_at = timezone.now()
            job.error_message = ""
            job.save(
                update_fields=[
                    "status",
                    "attempt_count",
                    "started_at",
                    "error_message",
                    "updated_at",
                ]
            )

            return job
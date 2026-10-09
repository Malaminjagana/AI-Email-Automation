
import logging

from django.db import transaction
from django.utils import timezone

from emails.models import EmailProcessingRecord


logger = logging.getLogger(__name__)


class DatabaseProcessingRecordStore:

    def claim(self, message_id: str) -> bool:
        """
        Atomically claim an email for processing.

        Returns True for a new or retryable failed record.
        Returns False if the email is already processing
        or has already completed.
        """

        if not message_id or not message_id.strip():
            raise ValueError("message_id must not be empty")

        now = timezone.now()

        with transaction.atomic():

            record, created = (
                EmailProcessingRecord.objects.get_or_create(
                    message_id=message_id,
                    defaults={
                        "status": EmailProcessingRecord.Status.PROCESSING,
                        "attempt_count": 1,
                        "started_at": now,
                    },
                )
            )

            if created:
                return True

            record = (
                EmailProcessingRecord.objects
                .select_for_update()
                .get(pk=record.pk)
            )

            if record.status in {
                EmailProcessingRecord.Status.PROCESSING,
                EmailProcessingRecord.Status.COMPLETED,
            }:
                return False

            record.status = EmailProcessingRecord.Status.PROCESSING
            record.attempt_count += 1
            record.error_message = ""
            record.started_at = now
            record.completed_at = None

            record.save(
                update_fields=[
                    "status",
                    "attempt_count",
                    "error_message",
                    "started_at",
                    "completed_at",
                    "updated_at",
                ]
            )

            return True

    def mark_completed(self, message_id: str) -> None:

        updated = EmailProcessingRecord.objects.filter(
            message_id=message_id,
            status=EmailProcessingRecord.Status.PROCESSING,
        ).update(
            status=EmailProcessingRecord.Status.COMPLETED,
            completed_at=timezone.now(),
            error_message="",
            updated_at=timezone.now(),
        )

        if updated != 1:
            raise RuntimeError(
                "Could not mark email processing as completed."
            )

    def mark_failed(
        self,
        message_id: str,
        error: Exception,
    ) -> None:

        # Store a bounded diagnostic message, not a full traceback.
        safe_message = (
            f"{type(error).__name__}: {error}"
        )[:1000]

        updated = EmailProcessingRecord.objects.filter(
            message_id=message_id,
            status=EmailProcessingRecord.Status.PROCESSING,
        ).update(
            status=EmailProcessingRecord.Status.FAILED,
            error_message=safe_message,
            updated_at=timezone.now(),
        )

        if updated != 1:
            logger.error(
                "Could not persist failed status for email %s",
                message_id,
            )
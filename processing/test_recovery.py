
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from emails.models import EmailProcessingJob
from processing.recovery import recover_stale_jobs


class StaleJobRecoveryTests(TestCase):

    def test_stale_job_returns_to_pending(self):
        started_at = timezone.now() - timedelta(
            minutes=15
        )

        job = EmailProcessingJob.objects.create(
            status="processing",
            processing_started_at=started_at,
        )

        recovered = recover_stale_jobs(
            timeout_minutes=10
        )

        job.refresh_from_db()

        self.assertEqual(recovered, 1)
        self.assertEqual(job.status, "pending")
        self.assertIsNone(job.processing_started_at)

    def test_recent_job_remains_processing(self):
        started_at = timezone.now() - timedelta(
            minutes=2
        )

        job = EmailProcessingJob.objects.create(
            status="processing",
            processing_started_at=started_at,
        )

        recovered = recover_stale_jobs(
            timeout_minutes=10
        )

        job.refresh_from_db()

        self.assertEqual(recovered, 0)
        self.assertEqual(job.status, "processing")

    def test_completed_job_is_not_recovered(self):
        job = EmailProcessingJob.objects.create(
            status="completed",
            processing_started_at=None,
        )

        recovered = recover_stale_jobs(
            timeout_minutes=10
        )

        job.refresh_from_db()

        self.assertEqual(recovered, 0)
        self.assertEqual(job.status, "completed")

    def test_invalid_timeout_is_rejected(self):
        with self.assertRaises(ValueError):
            recover_stale_jobs(timeout_minutes=0)
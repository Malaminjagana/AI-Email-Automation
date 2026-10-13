
from datetime import timedelta

from django.utils import timezone

from emails.models import EmailProcessingJob


def recover_stale_jobs(timeout_minutes: int = 10) -> int:
    """
    Return stale processing jobs to the pending queue.

    Assumes the model uses:
    - status="processing"
    - status="pending"
    - processing_started_at
    """
    if timeout_minutes <= 0:
        raise ValueError(
            "timeout_minutes must be greater than zero"
        )

    cutoff = timezone.now() - timedelta(
        minutes=timeout_minutes
    )

    stale_jobs = EmailProcessingJob.objects.filter(
        status="processing",
        processing_started_at__lt=cutoff,
    )

    recovered_count = stale_jobs.update(
        status="pending",
        processing_started_at=None,
    )

    return recovered_count
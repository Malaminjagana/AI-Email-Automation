
from datetime import timedelta
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.utils import timezone

from emails.models import EmailProcessingJob


pytestmark = pytest.mark.django_db


@pytest.fixture
def sample_email_path():
    return "sample_emails/order.eml"


def test_enqueue_command_creates_pending_job(sample_email_path):
    call_command("enqueue_email", sample_email_path)

    job = EmailProcessingJob.objects.get()

    assert job.source_path.endswith("sample_emails/order.eml")
    assert job.status == EmailProcessingJob.Status.PENDING
    assert job.attempt_count == 0


@patch("emails.management.commands.process_email_jobs.EmailProcessingPipeline")
def test_worker_completes_pending_job(
    mock_pipeline_class,
    sample_email_path,
):
    job = EmailProcessingJob.objects.create(
        source_path=sample_email_path,
    )

    mock_pipeline_class.return_value.process_file.return_value = object()

    call_command("process_email_jobs")

    job.refresh_from_db()

    assert job.status == EmailProcessingJob.Status.COMPLETED
    assert job.attempt_count == 1
    assert job.completed_at is not None
    mock_pipeline_class.return_value.process_file.assert_called_once_with(
        sample_email_path
    )


@patch("emails.management.commands.process_email_jobs.EmailProcessingPipeline")
def test_worker_records_failed_job(
    mock_pipeline_class,
    sample_email_path,
):
    job = EmailProcessingJob.objects.create(
        source_path=sample_email_path,
    )

    mock_pipeline_class.return_value.process_file.side_effect = (
        RuntimeError("Simulated processing failure")
    )

    call_command("process_email_jobs")

    job.refresh_from_db()

    assert job.status == EmailProcessingJob.Status.FAILED
    assert job.attempt_count == 1
    assert job.error_message == "RuntimeError"
    assert job.completed_at is None


@patch("emails.management.commands.process_email_jobs.EmailProcessingPipeline")
def test_worker_recovers_stale_job(
    mock_pipeline_class,
    sample_email_path,
):
    job = EmailProcessingJob.objects.create(
        source_path=sample_email_path,
        status=EmailProcessingJob.Status.PROCESSING,
        attempt_count=1,
        started_at=timezone.now() - timedelta(hours=1),
    )

    mock_pipeline_class.return_value.process_file.return_value = object()

    call_command(
        "process_email_jobs",
        recover_stale_minutes=10,
    )

    job.refresh_from_db()

    assert job.status == EmailProcessingJob.Status.COMPLETED
    assert job.attempt_count == 2
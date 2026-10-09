
import pytest

from emails.models import EmailProcessingRecord
from processing.records import DatabaseProcessingRecordStore


pytestmark = pytest.mark.django_db


def test_claim_creates_processing_record():

    store = DatabaseProcessingRecordStore()

    claimed = store.claim(
        "<day22-001@example.com>"
    )

    record = EmailProcessingRecord.objects.get(
        message_id="<day22-001@example.com>"
    )

    assert claimed is True
    assert record.status == EmailProcessingRecord.Status.PROCESSING
    assert record.attempt_count == 1
    assert record.started_at is not None


def test_completed_email_cannot_be_claimed_again():

    store = DatabaseProcessingRecordStore()

    message_id = "<day22-002@example.com>"

    assert store.claim(message_id) is True

    store.mark_completed(message_id)

    assert store.claim(message_id) is False

    record = EmailProcessingRecord.objects.get(
        message_id=message_id
    )

    assert record.status == EmailProcessingRecord.Status.COMPLETED
    assert record.attempt_count == 1
    assert record.completed_at is not None


def test_failed_email_can_be_retried():

    store = DatabaseProcessingRecordStore()

    message_id = "<day22-003@example.com>"

    assert store.claim(message_id) is True

    store.mark_failed(
        message_id,
        RuntimeError("Simulated ERP failure"),
    )

    assert store.claim(message_id) is True

    record = EmailProcessingRecord.objects.get(
        message_id=message_id
    )

    assert record.status == EmailProcessingRecord.Status.PROCESSING
    assert record.attempt_count == 2
    assert record.error_message == ""


def test_record_is_available_to_a_new_store_instance():

    message_id = "<day22-004@example.com>"

    first_store = DatabaseProcessingRecordStore()

    assert first_store.claim(message_id) is True

    first_store.mark_completed(message_id)

    second_store = DatabaseProcessingRecordStore()

    assert second_store.claim(message_id) is False


def test_empty_message_id_is_rejected():

    store = DatabaseProcessingRecordStore()

    with pytest.raises(
        ValueError,
        match="message_id must not be empty",
    ):
        store.claim("   ")
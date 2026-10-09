from processing.idempotency import IdempotencyStore


def test_message_id_is_not_processed_initially():

    store = IdempotencyStore()

    assert (
        store.has_been_processed(
            "<order-001@example.com>"
        )
        is False
    )


def test_message_id_can_be_marked_as_processed():

    store = IdempotencyStore()

    message_id = "<order-001@example.com>"

    store.mark_as_processed(
        message_id
    )

    assert (
        store.has_been_processed(
            message_id
        )
        is True
    )


def test_different_message_ids_are_tracked_separately():

    store = IdempotencyStore()

    first_id = "<order-001@example.com>"
    second_id = "<order-002@example.com>"

    store.mark_as_processed(first_id)

    assert (
        store.has_been_processed(first_id)
        is True
    )

    assert (
        store.has_been_processed(second_id)
        is False
    )
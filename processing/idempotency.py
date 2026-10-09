class IdempotencyStore:

    def __init__(self):
        self._processed_ids = set()

    def has_been_processed(
        self,
        message_id: str,
    ) -> bool:

        return message_id in self._processed_ids

    def mark_as_processed(
        self,
        message_id: str,
    ) -> None:

        self._processed_ids.add(message_id)

class IdempotencyStore:

    def __init__(self):
        self._statuses = {}

    def claim(self, message_id: str) -> bool:

        if not message_id or not message_id.strip():
            raise ValueError("message_id must not be empty")

        status = self._statuses.get(message_id)

        if status in {"processing", "completed"}:
            return False

        self._statuses[message_id] = "processing"

        return True

    def mark_completed(self, message_id: str) -> None:
        self._statuses[message_id] = "completed"

    def mark_failed(
        self,
        message_id: str,
        error: Exception,
    ) -> None:
        self._statuses[message_id] = "failed"

    def has_been_processed(self, message_id: str) -> bool:
        return self._statuses.get(message_id) == "completed"

    def mark_as_processed(self, message_id: str) -> None:
        self.mark_completed(message_id)
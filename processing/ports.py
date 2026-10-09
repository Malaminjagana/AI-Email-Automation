
from typing import Any, Protocol

from processing.validator import OrderSchema


class EmailReaderPort(Protocol):

    def read_file(self, file_path: str) -> bytes:
        ...


class EmailParserPort(Protocol):

    def parse(self, raw_email: bytes) -> dict[str, Any]:
        ...


class LLMPort(Protocol):

    def generate(self, prompt: str) -> str:
        ...


class OrderExtractorPort(Protocol):

    def extract(self, ai_response: str) -> OrderSchema:
        ...


class OrderDestinationPort(Protocol):

    def create_order(self, order: OrderSchema) -> dict[str, Any]:
        ...


class IdempotencyStorePort(Protocol):

    def has_been_processed(self, message_id: str) -> bool:
        ...

    def mark_as_processed(self, message_id: str) -> None:
        ...



class ProcessingRecordStorePort(Protocol):

    def claim(self, message_id: str) -> bool:
        ...

    def mark_completed(self, message_id: str) -> None:
        ...

    def mark_failed(
        self,
        message_id: str,
        error: Exception,
    ) -> None:
        ...



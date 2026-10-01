import json

from pydantic import ValidationError

from processing.validator import OrderSchema


class InvalidJSONError(Exception):
    """Raised when the LLM does not return valid JSON."""


class OrderValidationError(Exception):
    """Raised when the LLM JSON does not match OrderSchema."""

    def __init__(self, message, details=None):
        super().__init__(message)
        self.details = details or []


class OrderExtractor:

    def extract(self, ai_response: str) -> OrderSchema:

        try:
            data = json.loads(ai_response)

        except json.JSONDecodeError as exc:
            raise InvalidJSONError(
                "The LLM returned invalid JSON."
            ) from exc

        if not isinstance(data, dict):
            raise InvalidJSONError(
                "The LLM returned JSON, but it was not a JSON object."
            )

        try:
            return OrderSchema.model_validate(data)

        except ValidationError as exc:
            raise OrderValidationError(
                "The LLM response failed order validation.",
                exc.errors(),
            ) from exc

        
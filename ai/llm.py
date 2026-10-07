import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


logger = logging.getLogger(__name__)


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")



class LLMTemporaryError(Exception):
    """Raised when the LLM request fails temporarily."""
    pass


class LLMService:

    def __init__(self):
        self.client = genai.Client()

    def generate(self, prompt: str) -> str:
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )

            return response.text

        except Exception as exc:
            raise LLMTemporaryError(
                "The LLM request failed temporarily."
            ) from exc


class LLMServiceError(Exception):
    """Raised when the LLM service cannot process a request."""


class LLMService:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=api_key
        )

    def generate(self, prompt: str) -> str:

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )

        except Exception as exc:
            logger.exception(
                "LLM request failed."
            )

            raise LLMServiceError(
                "The LLM service could not process the request."
            ) from exc

        if not response.text:
            raise LLMServiceError(
                "The LLM returned an empty response."
            )

        return response.text
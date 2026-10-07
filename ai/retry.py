import logging
import time

from ai.llm import LLMTemporaryError


logger = logging.getLogger(__name__)


def generate_with_retry(
    llm,
    prompt: str,
    max_attempts: int = 3,
    delay_seconds: int = 2,
) -> str:

    for attempt in range(1, max_attempts + 1):

        try:

            logger.info(
                "LLM attempt %s/%s",
                attempt,
                max_attempts,
            )

            return llm.generate(prompt)

        except LLMTemporaryError as exc:

            logger.warning(
                "LLM attempt %s failed: %s",
                attempt,
                exc,
            )

            if attempt == max_attempts:

                logger.error(
                    "LLM failed after %s attempts.",
                    max_attempts,
                )

                raise

            logger.info(
                "Waiting %s seconds before retry.",
                delay_seconds,
            )

            time.sleep(delay_seconds)
import pytest

from ai.llm import LLMTemporaryError
from ai.retry import generate_with_retry


class FakeLLM:

    def __init__(self):
        self.calls = 0

    def generate(self, prompt):
        self.calls += 1

        if self.calls < 3:
            raise LLMTemporaryError(
                "Temporary failure"
            )

        return "success"


class AlwaysFailingLLM:

    def __init__(self):
        self.calls = 0

    def generate(self, prompt):
        self.calls += 1

        raise LLMTemporaryError(
            "Temporary failure"
        )


def test_retry_succeeds_after_temporary_failures():

    llm = FakeLLM()

    result = generate_with_retry(
        llm,
        "test prompt",
        max_attempts=3,
        delay_seconds=0,
    )

    assert result == "success"
    assert llm.calls == 3


def test_retry_fails_after_max_attempts():

    llm = AlwaysFailingLLM()

    with pytest.raises(LLMTemporaryError):

        generate_with_retry(
            llm,
            "test prompt",
            max_attempts=3,
            delay_seconds=0,
        )

    assert llm.calls == 3


def test_retry_logs_failed_attempt(caplog):

    llm = AlwaysFailingLLM()

    with caplog.at_level("WARNING"):

        with pytest.raises(LLMTemporaryError):

            generate_with_retry(
                llm,
                "test prompt",
                max_attempts=2,
                delay_seconds=0,
            )

    assert "LLM attempt 1 failed" in caplog.text
      
import logging

from django.http import JsonResponse

from ai.extractor import (
    InvalidJSONError,
    OrderValidationError,
)
from ai.llm import LLMServiceError
from processing.pipeline import EmailProcessingPipeline


logger = logging.getLogger(__name__)


def health_check(request):
    return JsonResponse({
        "status": "ok",
        "message": "AI Email Automation API is running"
    })


def read_test_email(request):
    from .services import EmailReader, EmailParser

    reader = EmailReader()
    parser = EmailParser()

    raw_email = reader.read_file(
        "sample_emails/order.eml"
    )

    email_data = parser.parse(raw_email)

    return JsonResponse(email_data)


def analyze_test_email(request):

    pipeline = EmailProcessingPipeline()

    try:

        result = pipeline.process_file(
            "sample_emails/order.eml"
        )

        return JsonResponse({
            "email": result.email,
            "ai_response": result.ai_response,
            "validated_order": (
                result.validated_order.model_dump()
            ),
            "crm_order": result.crm_order,
        })

    except LLMServiceError as exc:

        logger.warning(
            "LLM service error: %s",
            exc,
        )

        return JsonResponse(
            {
                "error": {
                    "type": "llm_error",
                    "message": str(exc),
                }
            },
            status=502,
        )

    except InvalidJSONError as exc:

        logger.warning(
            "Invalid JSON from LLM: %s",
            exc,
        )

        return JsonResponse(
            {
                "error": {
                    "type": "invalid_json",
                    "message": str(exc),
                }
            },
            status=502,
        )

    except OrderValidationError as exc:

        logger.warning(
            "Order validation failed: %s",
            exc,
        )

        return JsonResponse(
            {
                "error": {
                    "type": "validation_error",
                    "message": str(exc),
                    "details": exc.details,
                }
            },
            status=422,
        )

    except Exception:

        logger.exception(
            "Unexpected error while analyzing email."
        )

        return JsonResponse(
            {
                "error": {
                    "type": "internal_error",
                    "message": (
                        "An unexpected error occurred."
                    ),
                }
            },
            status=500,
        )
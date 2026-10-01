
# Automated testes command python3 -m pytest -v
# python3 manage.py check

from django.test import Client

from ai.extractor import (
    InvalidJSONError,
    OrderValidationError,
)

from processing.validator import OrderSchema


def test_analyze_endpoint_returns_success(monkeypatch):

    fake_order = OrderSchema(
        customer="Test GmbH",
        product="Laptop",
        quantity=25,
        delivery_location="Berlin",
    )

    fake_result = {
        "email": {
            "sender": "test@example.com",
            "subject": "Test order",
            "body": "Test email",
        },
        "ai_response": (
            '{"customer":"Test GmbH",'
            '"product":"Laptop",'
            '"quantity":25,'
            '"delivery_location":"Berlin"}'
        ),
        "validated_order": fake_order,
    }

    class FakePipeline:

        def process_file(self, file_path: str):
            return fake_result

    monkeypatch.setattr(
        "emails.views.EmailProcessingPipeline",
        FakePipeline,
    )

    client = Client()

    response = client.get(
        "/emails/analyze/"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["validated_order"]["customer"] == "Test GmbH"
    assert data["validated_order"]["quantity"] == 25


def test_analyze_endpoint_handles_invalid_json(monkeypatch):

    class FakePipeline:

        def process_file(self, file_path: str):
            raise InvalidJSONError(
                "The LLM returned invalid JSON."
            )

    monkeypatch.setattr(
        "emails.views.EmailProcessingPipeline",
        FakePipeline,
    )

    client = Client()

    response = client.get(
        "/emails/analyze/"
    )

    assert response.status_code == 502

    data = response.json()

    assert data["error"]["type"] == "invalid_json"


def test_analyze_endpoint_handles_validation_error(
    monkeypatch
):

    class FakePipeline:

        def process_file(self, file_path: str):
            raise OrderValidationError(
                "The LLM response failed order validation.",
                [],
            )

    monkeypatch.setattr(
        "emails.views.EmailProcessingPipeline",
        FakePipeline,
    )

    client = Client()

    response = client.get(
        "/emails/analyze/"
    )

    assert response.status_code == 422

    data = response.json()

    assert (
        data["error"]["type"]
        == "validation_error"
    )
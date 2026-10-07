# Automated testes command python3 -m pytest -v
# python3 manage.py runserver

import json

from processing.pipeline import EmailProcessingPipeline


def test_pipeline_processes_email_without_real_llm(monkeypatch):

    fake_ai_response = json.dumps({
        "customer": "Test GmbH",
        "product": "Laptop",
        "quantity": 25,
        "delivery_location": "Berlin",
    })


    class FakeLLMService:

        def generate(self, prompt: str) -> str:
            return fake_ai_response


    monkeypatch.setattr(
        "processing.pipeline.LLMService",
        FakeLLMService,
    )


    pipeline = EmailProcessingPipeline()

    result = pipeline.process_file(
        "sample_emails/order.eml"
    )


    order = result["validated_order"]


    assert order.customer == "Test GmbH"
    assert order.product == "Laptop"
    assert order.quantity == 25
    assert order.delivery_location == "Berlin"

def test_pipeline_sends_validated_order_to_crm(monkeypatch):

    crm_calls = []

    class FakeCRM:

        def create_order(self, order):

            crm_calls.append(order)

            return {
                "customer": order.customer,
                "product": order.product,
                "quantity": order.quantity,
                "delivery_location": order.delivery_location,
            }

    monkeypatch.setattr(
        "processing.pipeline.CRMService",
        FakeCRM,
    )

    # Re-create the pipeline after replacing CRMService.
    pipeline = EmailProcessingPipeline()

    result = pipeline.process_file(
        "sample_emails/order.eml"
    )

    assert len(crm_calls) == 1

    assert crm_calls[0].customer == "Müller GmbH"

    assert result.crm_order["customer"] == "Müller GmbH"
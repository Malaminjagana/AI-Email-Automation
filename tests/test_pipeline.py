# Automated testes command python3 -m pytest -v
# python3 manage.py check

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
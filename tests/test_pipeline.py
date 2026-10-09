# Automated tests command:
# python3 -m pytest -v
# python3 manage.py runserver

import json
import pytest
from processing.pipeline import EmailProcessingPipeline


def test_pipeline_processes_email_without_real_llm(
    monkeypatch
):

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

    order = result.validated_order

    assert order.customer == "Test GmbH"
    assert order.product == "Laptop"
    assert order.quantity == 25
    assert order.delivery_location == "Berlin"


def test_pipeline_sends_validated_order_to_crm(
    monkeypatch
):

    fake_ai_response = json.dumps({
        "customer": "Müller GmbH",
        "product": "Product A",
        "quantity": 50,
        "delivery_location": "Berlin",
    })

    class FakeLLMService:

        def generate(self, prompt: str) -> str:
            return fake_ai_response

    monkeypatch.setattr(
        "processing.pipeline.LLMService",
        FakeLLMService,
    )

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

    pipeline = EmailProcessingPipeline()

    result = pipeline.process_file(
        "sample_emails/order.eml"
    )

    assert len(crm_calls) == 1

    assert crm_calls[0].customer == "Müller GmbH"

    assert (
        result.crm_order["customer"]
        == "Müller GmbH"
    )


def test_pipeline_sends_validated_order_to_erp(
    monkeypatch
):

    fake_ai_response = json.dumps({
        "customer": "Müller GmbH",
        "product": "Product A",
        "quantity": 50,
        "delivery_location": "Berlin",
    })

    class FakeLLMService:

        def generate(self, prompt: str) -> str:
            return fake_ai_response

    monkeypatch.setattr(
        "processing.pipeline.LLMService",
        FakeLLMService,
    )

    erp_calls = []

    class FakeERP:

        def create_order(self, order):

            erp_calls.append(order)

            return {
                "customer": order.customer,
                "product": order.product,
                "quantity": order.quantity,
                "delivery_location": order.delivery_location,
            }

    monkeypatch.setattr(
        "processing.pipeline.ERPService",
        FakeERP,
    )

    pipeline = EmailProcessingPipeline()

    result = pipeline.process_file(
        "sample_emails/order.eml"
    )

    assert len(erp_calls) == 1

    assert erp_calls[0].customer == "Müller GmbH"

    assert (
        result.erp_order["customer"]
        == "Müller GmbH"
    )
def test_pipeline_does_not_process_same_email_twice(
    monkeypatch
):

    fake_ai_response = json.dumps({
        "customer": "Müller GmbH",
        "product": "Product A",
        "quantity": 50,
        "delivery_location": "Berlin",
    })

    class FakeLLMService:

        def generate(self, prompt: str) -> str:
            return fake_ai_response

    monkeypatch.setattr(
        "processing.pipeline.LLMService",
        FakeLLMService,
    )

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

    erp_calls = []

    class FakeERP:

        def create_order(self, order):

            erp_calls.append(order)

            return {
                "customer": order.customer,
                "product": order.product,
                "quantity": order.quantity,
                "delivery_location": order.delivery_location,
            }

    monkeypatch.setattr(
        "processing.pipeline.ERPService",
        FakeERP,
    )

    pipeline = EmailProcessingPipeline()

    first_result = pipeline.process_file(
        "sample_emails/order.eml"
    )

    second_result = pipeline.process_file(
        "sample_emails/order.eml"
    )

    assert first_result is not None

    assert second_result is None

def test_pipeline_reports_erp_failure_after_crm_success(
    monkeypatch
):
    fake_ai_response = json.dumps({
        "customer": "Müller GmbH",
        "product": "Product A",
        "quantity": 50,
        "delivery_location": "Berlin",
    })

    class FakeLLMService:

        def generate(self, prompt: str) -> str:
            return fake_ai_response

    monkeypatch.setattr(
        "processing.pipeline.LLMService",
        FakeLLMService,
    )

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

    erp_calls = []

    class FakeERP:

        def create_order(self, order):
            erp_calls.append(order)

            raise RuntimeError(
                "Simulated ERP connection failure"
            )

    monkeypatch.setattr(
        "processing.pipeline.ERPService",
        FakeERP,
    )

    pipeline = EmailProcessingPipeline()

    with pytest.raises(
        RuntimeError,
        match="Simulated ERP connection failure",
    ):
        pipeline.process_file(
            "sample_emails/order.eml"
        )

    assert len(crm_calls) == 1
    assert len(erp_calls) == 1







    assert len(crm_calls) == 1

    assert len(erp_calls) == 1
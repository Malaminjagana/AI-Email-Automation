
import json

from processing.idempotency import IdempotencyStore
from processing.pipeline import EmailProcessingPipeline


class FakeReader:

    def __init__(self):
        self.file_paths = []

    def read_file(self, file_path: str) -> bytes:
        self.file_paths.append(file_path)
        return b"fake email content"


class FakeParser:

    def parse(self, raw_email: bytes) -> dict:
        assert raw_email == b"fake email content"

        return {
            "message_id": "<injected-001@example.com>",
            "sender": "customer@example.com",
            "recipient": "orders@example.com",
            "subject": "Test order",
            "date": "2026-10-09",
            "body": "Order 25 laptops for Berlin.",
        }


class FakeLLM:

    def generate(self, prompt: str) -> str:
        assert "Order 25 laptops for Berlin." in prompt

        return json.dumps({
            "customer": "Test GmbH",
            "product": "Laptop",
            "quantity": 25,
            "delivery_location": "Berlin",
        })


class FakeDestination:

    def __init__(self):
        self.orders = []

    def create_order(self, order):

        self.orders.append(order)

        return {
            "customer": order.customer,
            "product": order.product,
            "quantity": order.quantity,
            "delivery_location": order.delivery_location,
        }


def test_pipeline_uses_injected_dependencies():

    reader = FakeReader()
    parser = FakeParser()
    llm = FakeLLM()
    crm = FakeDestination()
    erp = FakeDestination()

    pipeline = EmailProcessingPipeline(
        reader=reader,
        parser=parser,
        llm=llm,
        crm=crm,
        erp=erp,
        idempotency_store=IdempotencyStore(),
    )

    result = pipeline.process_file("virtual-order.eml")

    assert result is not None

    assert reader.file_paths == ["virtual-order.eml"]

    assert result.validated_order.customer == "Test GmbH"
    assert result.validated_order.quantity == 25

    assert len(crm.orders) == 1
    assert len(erp.orders) == 1

    assert result.crm_order["customer"] == "Test GmbH"
    assert result.erp_order["customer"] == "Test GmbH"
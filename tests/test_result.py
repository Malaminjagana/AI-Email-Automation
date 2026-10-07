import pytest
from pydantic import ValidationError

from processing.result import ProcessingResult
from processing.validator import OrderSchema


def test_processing_result_accepts_valid_data():

    order = OrderSchema(
        customer="Test GmbH",
        product="Laptop",
        quantity=25,
        delivery_location="Berlin",
    )

    result = ProcessingResult(
        email={
            "sender": "jaganalamin@gmail.com",
            "subject": "Test order",
            "body": "Test email",
        },
        ai_response='{"customer":"Test GmbH"}',
        validated_order=order,
    )

    assert result.email["sender"] == "jaganalamin@gmail.com"
    assert result.ai_response.startswith("{")
    assert result.validated_order.customer == "Test GmbH"
    assert result.validated_order.quantity == 25


def test_processing_result_rejects_invalid_order():

    with pytest.raises(ValidationError):

        ProcessingResult(
            email={
                "sender": "jaganalamin@gmail.com",
            },
            ai_response="invalid",
            validated_order={
                "customer": "",
                "product": "Laptop",
                "quantity": 25,
                "delivery_location": "Berlin",
            },
        )
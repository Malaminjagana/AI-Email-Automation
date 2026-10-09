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
            "sender": "test@example.com",
            "subject": "Test order",
            "body": "Test email",
        },
        ai_response='{"customer":"Test GmbH"}',
        validated_order=order,
        crm_order={
            "customer": "Test GmbH",
            "product": "Laptop",
            "quantity": 25,
            "delivery_location": "Berlin",
        },
        erp_order={
            "customer": "Test GmbH",
            "product": "Laptop",
            "quantity": 25,
            "delivery_location": "Berlin",
        },
    )

    assert result.email["sender"] == "test@example.com"
    assert result.ai_response.startswith("{")
    assert result.validated_order.customer == "Test GmbH"
    assert result.validated_order.quantity == 25
    assert result.crm_order["customer"] == "Test GmbH"
    assert result.erp_order["customer"] == "Test GmbH"


def test_processing_result_rejects_invalid_order():

    with pytest.raises(ValidationError):

        ProcessingResult(
            email={
                "sender": "test@example.com",
            },
            ai_response="invalid",
            validated_order={
                "customer": "",
                "product": "Laptop",
                "quantity": 25,
                "delivery_location": "Berlin",
            },
            crm_order={
                "customer": "Test GmbH",
                "product": "Laptop",
                "quantity": 25,
                "delivery_location": "Berlin",
            },
            erp_order={
                "customer": "Test GmbH",
                "product": "Laptop",
                "quantity": 25,
                "delivery_location": "Berlin",
            },
        )
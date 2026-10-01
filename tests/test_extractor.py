# Automated testes command python3 -m pytest -v
# python3 manage.py check
import pytest

from ai.extractor import (
    InvalidJSONError,
    OrderExtractor,
    OrderValidationError,
)


def test_valid_json_is_extracted():
    extractor = OrderExtractor()

    ai_response = """
    {
        "customer": "Test GmbH",
        "product": "Laptop",
        "quantity": 10,
        "delivery_location": "Berlin"
    }
    """

    order = extractor.extract(ai_response)

    assert order.customer == "Test GmbH"
    assert order.product == "Laptop"
    assert order.quantity == 10
    assert order.delivery_location == "Berlin"


def test_invalid_json_raises_error():
    extractor = OrderExtractor()

    ai_response = """
    This is not valid JSON.
    """

    with pytest.raises(InvalidJSONError):
        extractor.extract(ai_response)


def test_json_array_is_rejected():
    extractor = OrderExtractor()

    ai_response = """
    [
        "Test GmbH",
        "Laptop"
    ]
    """

    with pytest.raises(InvalidJSONError):
        extractor.extract(ai_response)


def test_invalid_order_raises_validation_error():
    extractor = OrderExtractor()

    ai_response = """
    {
        "customer": "Test GmbH",
        "product": "Laptop",
        "quantity": -10,
        "delivery_location": "Berlin"
    }
    """

    with pytest.raises(OrderValidationError):
        extractor.extract(ai_response)
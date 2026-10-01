# Automated testes command python3 -m pytest -v
# python3 manage.py check

import pytest
from pydantic import ValidationError

from processing.validator import OrderSchema


def test_valid_order():
    order = OrderSchema(
        customer="Müller GmbH",
        product="Product A",
        quantity=50,
        delivery_location="Berlin",
    )

    assert order.customer == "Müller GmbH"
    assert order.product == "Product A"
    assert order.quantity == 50
    assert order.delivery_location == "Berlin"


def test_quantity_must_be_positive():
    with pytest.raises(ValidationError):
        OrderSchema(
            customer="Müller GmbH",
            product="Product A",
            quantity=0,
            delivery_location="Berlin",
        )


def test_negative_quantity_is_invalid():
    with pytest.raises(ValidationError):
        OrderSchema(
            customer="Müller GmbH",
            product="Product A",
            quantity=-10,
            delivery_location="Berlin",
        )


def test_quantity_must_be_integer():
    with pytest.raises(ValidationError):
        OrderSchema(
            customer="Müller GmbH",
            product="Product A",
            quantity="50",
            delivery_location="Berlin",
        )


def test_extra_fields_are_rejected():
    with pytest.raises(ValidationError):
        OrderSchema(
            customer="Müller GmbH",
            product="Product A",
            quantity=50,
            delivery_location="Berlin",
            confidence=0.99,
        )
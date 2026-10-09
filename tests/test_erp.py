import pytest

from integrations.erp import ERPService
from processing.validator import OrderSchema


def test_erp_creates_order():

    order = OrderSchema(
        customer="Müller GmbH",
        product="Product A",
        quantity=50,
        delivery_location="Berlin",
    )

    erp = ERPService()

    result = erp.create_order(order)

    assert result["customer"] == "Müller GmbH"
    assert result["product"] == "Product A"
    assert result["quantity"] == 50
    assert result["delivery_location"] == "Berlin"


def test_erp_stores_created_order():

    order = OrderSchema(
        customer="Test GmbH",
        product="Laptop",
        quantity=10,
        delivery_location="Berlin",
    )

    erp = ERPService()

    erp.create_order(order)

    assert len(erp.orders) == 1
    assert erp.orders[0]["customer"] == "Test GmbH"


def test_erp_requires_validated_order():

    erp = ERPService()

    with pytest.raises(Exception):

        erp.create_order({
            "customer": "Test GmbH",
            "product": "Laptop",
            "quantity": 10,
            "delivery_location": "Berlin",
        })
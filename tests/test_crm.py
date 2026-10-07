import pytest

from integrations.crm import CRMService
from processing.validator import OrderSchema


def test_crm_creates_order():

    order = OrderSchema(
        customer="Müller GmbH",
        product="Product A",
        quantity=50,
        delivery_location="Berlin",
    )

    crm = CRMService()

    result = crm.create_order(order)

    assert result["customer"] == "Müller GmbH"
    assert result["product"] == "Product A"
    assert result["quantity"] == 50
    assert result["delivery_location"] == "Berlin"


def test_crm_stores_created_order():

    order = OrderSchema(
        customer="Test GmbH",
        product="Laptop",
        quantity=10,
        delivery_location="Berlin",
    )

    crm = CRMService()

    crm.create_order(order)

    assert len(crm.orders) == 1
    assert crm.orders[0]["customer"] == "Test GmbH"


def test_crm_requires_validated_order():

    crm = CRMService()

    with pytest.raises(Exception):

        crm.create_order({
            "customer": "Test GmbH",
            "product": "Laptop",
            "quantity": 10,
            "delivery_location": "Berlin",
        })
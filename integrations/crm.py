from processing.validator import OrderSchema


class CRMService:

    def __init__(self):
        self.orders = []

    def create_order(self, order: OrderSchema) -> dict:

        crm_order = {
            "customer": order.customer,
            "product": order.product,
            "quantity": order.quantity,
            "delivery_location": order.delivery_location,
        }

        self.orders.append(crm_order)

        return crm_order
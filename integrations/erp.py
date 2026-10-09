from processing.validator import OrderSchema


class ERPService:

    def __init__(self):
        self.orders = []

    def create_order(self, order: OrderSchema) -> dict:

        erp_order = {
            "customer": order.customer,
            "product": order.product,
            "quantity": order.quantity,
            "delivery_location": order.delivery_location,
        }

        self.orders.append(erp_order)

        return erp_order
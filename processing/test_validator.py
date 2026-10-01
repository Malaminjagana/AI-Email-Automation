from processing.validator import OrderSchema


order = OrderSchema(
    customer="Malamin Jagana ",
    product="Freelancer",
    quantity=150,
    delivery_location="Berlin",
)

print(order)
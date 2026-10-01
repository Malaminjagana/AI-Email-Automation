from pydantic import BaseModel, ConfigDict, Field, StrictInt


class OrderSchema(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    customer: str

    product: str

    quantity: StrictInt = Field(
        gt=0
    )

    delivery_location: str
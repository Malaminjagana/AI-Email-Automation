from pydantic import BaseModel, ConfigDict, Field, StrictInt


class OrderSchema(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    customer: str = Field(
        min_length=1
    )

    product: str = Field(
        min_length=1
    )

    quantity: StrictInt = Field(
        gt=0
    )

    delivery_location: str = Field(
        min_length=1
    )

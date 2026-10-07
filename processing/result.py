from pydantic import BaseModel

from processing.validator import OrderSchema


class ProcessingResult(BaseModel):

    email: dict
    ai_response: str
    validated_order: OrderSchema
    crm_order: dict 
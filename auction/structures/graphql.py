from pydantic import BaseModel, validator

from decimal import Decimal
from auction.models import Client
import traceback


class Structure(BaseModel):
    class Config:
        arbitrary_types_allowed = True


class BidInput(Structure):
    client: Client
    price: Decimal
    product_id: int

    @validator("price")
    def check_price(cls, v):
        if v <= 0:
            raise ValueError("price must be greater than 0")
        return v

    @validator("product_id")
    def check_product_id(cls, v):
        if v <= 0:
            raise ValueError("id must be positive")
        return v

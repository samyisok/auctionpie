from pydantic import BaseModel, validator

from decimal import Decimal
from auction.models import Client
import datetime
from typing import Union, Optional


def _is_positive(
    v: Union[Decimal, int, float],
    msg: str,
) -> Union[Decimal, int, float]:
    if v <= 0:
        raise ValueError(msg)
    return v


class Structure(BaseModel):
    class Config:
        arbitrary_types_allowed = True


class BidInput(Structure):
    client: Client
    price: Decimal
    product_id: int

    @validator("price")
    def check_price(cls, v):
        return _is_positive(v, "price must be greater than 0")

    @validator("product_id")
    def check_product_id(cls, v):
        return _is_positive(v, "id must be positive")


class ProductInput(Structure):
    seller: Client
    name: str
    description: str
    start_price: Decimal
    buy_price: Optional[Decimal]
    end_date: datetime.datetime
    start_date: Optional[datetime.datetime]

    @validator("start_price")
    def check_start_price(cls, v):
        return _is_positive(v, "price must be greater than 0")

    @validator("buy_price")
    def check_buy_price(cls, v, values, **kwargs):
        if v is None:
            return v
        if v <= values["start_price"]:
            raise ValueError("buy_price should be greater than start_price")
        return _is_positive(v, "price must be greater than 0")

    @validator("start_date")
    def check_date(cls, v, values, **kwargs):
        if v is None:
            return v
        if v >= values["end_date"]:
            raise ValueError("start_date should be lesser than end_date")
        return v

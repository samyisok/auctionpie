from datetime import datetime
from decimal import Decimal
from typing import Optional, Any, Dict

from pydantic import BaseModel, validator

from auction.models import Client


def _is_positive(v: Decimal, msg: str) -> Decimal:
    if v <= 0:
        raise ValueError(msg)
    return v


def _is_id(v: int, msg: str) -> int:
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
    def check_price(cls, v: Decimal) -> Decimal:
        return _is_positive(v, "price must be greater than 0")

    @validator("product_id")
    def check_product_id(cls, v: int) -> int:
        return _is_id(v, "id must be positive")


class ProductInput(Structure):
    seller: Client
    name: str
    description: str
    start_price: Decimal
    buy_price: Optional[Decimal]
    end_date: datetime
    start_date: datetime

    @validator("start_price")
    def check_start_price(cls, v: Decimal) -> Decimal:
        return _is_positive(v, "price must be greater than 0")

    @validator("buy_price")
    def check_buy_price(
        cls,
        v: Optional[Decimal],
        values: Dict[str, Any],
        **kwargs: Dict[str, Any],
    ) -> Optional[Decimal]:
        if v is None:
            return v
        if v <= values["start_price"]:
            raise ValueError("buy_price should be greater than start_price")
        return _is_positive(v, "price must be greater than 0")

    @validator("start_date")
    def check_date(
        cls, v: datetime, values: Dict[str, Any], **kwargs: Dict[str, Any]
    ) -> datetime:
        if v >= values["end_date"]:
            raise ValueError("start_date should be lesser than end_date")
        return v


class ProductUpdateInput(Structure):
    seller: Client
    product_id: int
    name: Optional[str]
    description: Optional[str]
    start_price: Optional[Decimal]
    buy_price: Optional[Decimal]
    end_date: Optional[datetime]
    start_date: Optional[datetime]

    # TODO check name and desc
    @validator("product_id")
    def check_product_id(cls, v: int) -> int:
        return _is_id(v, "price must be greater than 0")

    @validator("start_price")
    def check_start_price(cls, v: Decimal) -> Decimal:
        if v is None:
            return v
        return _is_positive(v, "price must be greater than 0")

    @validator("buy_price")
    def check_buy_price(
        cls,
        v: Optional[Decimal],
        values: Dict[str, Any],
        **kwargs: Dict[str, Any],
    ) -> Optional[Decimal]:
        if v is None:
            return v
        if v <= values["start_price"]:
            raise ValueError("buy_price should be greater than start_price")
        return _is_positive(v, "price must be greater than 0")

    @validator("start_date")
    def check_date(
        cls,
        v: Optional[datetime],
        values: Dict[str, Any],
        **kwargs: Dict[str, Any],
    ) -> Optional[datetime]:
        if v is None:
            return v
        if v >= values["end_date"]:
            raise ValueError("start_date should be lesser than end_date")
        return v


class ProductActionInput(Structure):
    """ Тип для разных действий где требуется только ID """

    seller: Client
    product_id: int


class PageListInput(Structure):
    """ Тип для для листинга с паджинацией, без авторизации """

    page: int
    page_size: int


class IdInput(Structure):
    """ Тип для queries с id """

    id: int

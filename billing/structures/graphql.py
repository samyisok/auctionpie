from decimal import Decimal

from pydantic import BaseModel

from auction.models import Client


class Structure(BaseModel):
    class Config:
        arbitrary_types_allowed = True


class ClientInput(Structure):
    """ Client input """

    client: Client


class PaymentInfoInput(ClientInput):
    """ payment info """

    payment_id: int


class CreatePaymentInput(ClientInput):
    """ payment info """

    payment_system: str
    amount: Decimal

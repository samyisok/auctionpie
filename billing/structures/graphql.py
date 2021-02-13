from pydantic import BaseModel

from auction.models import Client


class Structure(BaseModel):
    class Config:
        arbitrary_types_allowed = True


class ClientInput(Structure):
    """ Client input """

    client: Client

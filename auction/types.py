from graphene_django.types import DjangoObjectType

from .models import Bid, Client, Product


class ClientType(DjangoObjectType):
    class Meta:
        model = Client
        convert_choices_to_enum = False
        exclude = ["password"]


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"


class BidType(DjangoObjectType):
    class Meta:
        model = Bid
        fields = "__all__"

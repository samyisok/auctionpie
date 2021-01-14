import graphene

from .models import Client
from .types import ClientType


class Query(graphene.ObjectType):
    clients = graphene.List(ClientType)

    def resolve_clients(self, info):
        return Client.objects.all()


schema = graphene.Schema(query=Query)

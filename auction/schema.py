import graphene

from .models import Client
from .types import ClientType
from .mutations import RegistrationClient
from graphql_jwt.decorators import login_required


class Query(graphene.ObjectType):
    clients = graphene.List(ClientType)

    # TODO remove
    @login_required
    def resolve_clients(self, info):
        return Client.objects.all()


class Mutation(graphene.ObjectType):
    registration_client = RegistrationClient.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)

import graphene

from .types import ClientType
from .models import Client


class RegistrationClient(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    client = graphene.Field(ClientType)

    def mutate(self, info, email, password):
        client = Client.objects.create_user(email=email, password=password)
        return RegistrationClient(client=client)
import graphene
from graphql_jwt.decorators import login_required

from billing.helpers.graphql import get_balance
from billing.structures.graphql import ClientInput


class Query(graphene.ObjectType):
    balance = graphene.Decimal()

    @login_required
    def resolve_balance(self, info):
        """
        Получаем баланс
        """
        client = info.context.user
        client_input = ClientInput(client=client)
        return get_balance(input=client_input)


schema = graphene.Schema(query=Query)

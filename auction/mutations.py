import graphene
from graphql import GraphQLError
from .types import ClientType, ProductType
from .models import Client
from .helpers import graphql as graphql_helper
from graphql_jwt.decorators import login_required


class CreateProduct(graphene.Mutation):
    """
    Создание и выставление продукта на аукцион.
    """

    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        start_price = graphene.Decimal(required=True)
        buy_price = graphene.Decimal()
        start_date = graphene.DateTime(required=False)
        end_date = graphene.DateTime(required=True)

    product = graphene.Field(ProductType)

    @login_required
    def mutate(
        self,
        info,
        name,
        description,
        start_price,
        buy_price,
        end_date,
        start_date=None,
    ):
        client = info.context.user
        if isinstance(client, Client) is not True:
            raise GraphQLError("Should be client model")

        product = graphql_helper.create_new_product(
            client, name, description, start_price, buy_price, start_date, end_date
        )
        return CreateProduct(product=product)

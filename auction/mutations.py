import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from .helpers import graphql as graphql_helper
from .models import Client
from .structures.graphql import BidInput, ProductDeleteInput, ProductInput
from .types import BidType, ProductType


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
        end_date,
        buy_price=None,
        start_date=None,
    ):
        client = info.context.user
        if isinstance(client, Client) is not True:
            raise GraphQLError("Should be client model")

        product_input = ProductInput(
            seller=client,
            name=name,
            description=description,
            start_price=start_price,
            buy_price=buy_price,
            start_date=start_date,
            end_date=end_date,
        )

        product = graphql_helper.create_new_product(product_input)
        return CreateProduct(product=product)


class DeleteProduct(graphene.Mutation):
    """
    Отмена продукта
    """

    class Arguments:
        product_id = graphene.ID(required=True)

    product = graphene.Field(ProductType)

    @login_required
    def mutate(self, info, product_id):
        client = info.context.user

        if isinstance(client, Client) is not True:
            raise GraphQLError("Should be client model")

        product_delete_input = ProductDeleteInput(
            product_id=product_id,
        )

        product = graphql_helper.delete_product(product_delete_input)
        return DeleteProduct(product=product)


class CreateBid(graphene.Mutation):
    """
    создание ставки на товар
    """

    class Arguments:
        price = graphene.Decimal(required=True)
        product_id = graphene.ID(required=True)

    bid = graphene.Field(BidType)

    @login_required
    def mutate(self, info, price, product_id):
        client = info.context.user
        bid_input = BidInput(
            client=client,
            price=price,
            product_id=product_id,
        )

        bid = graphql_helper.create_bid(bid_input)
        return CreateBid(bid=bid)

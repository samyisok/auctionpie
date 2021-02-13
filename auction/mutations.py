import graphene
from graphql_jwt.decorators import login_required

from .helpers import graphql as graphql_helper
from .structures.graphql import (
    BidInput,
    ProductActionInput,
    ProductInput,
    ProductUpdateInput,
)
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


class UpdateProduct(graphene.Mutation):
    """
    Изменение продукта
    """

    class Arguments:
        product_id = graphene.ID(required=True)
        name = graphene.String(required=False)
        description = graphene.String(required=False)
        start_price = graphene.Decimal(required=False)
        buy_price = graphene.Decimal(required=False)
        start_date = graphene.DateTime(required=False)
        end_date = graphene.DateTime(required=False)

    product = graphene.Field(ProductType)

    @login_required
    def mutate(
        self,
        info,
        product_id,
        name=None,
        description=None,
        start_price=None,
        end_date=None,
        buy_price=None,
        start_date=None,
    ):
        client = info.context.user

        product_update_input = ProductUpdateInput(
            seller=client,
            product_id=product_id,
            name=name,
            description=description,
            start_price=start_price,
            buy_price=buy_price,
            start_date=start_date,
            end_date=end_date,
        )

        product = graphql_helper.update_product(product_update_input)
        return UpdateProduct(product=product)


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

        product_delete_input = ProductActionInput(
            seller=client,
            product_id=product_id,
        )

        product = graphql_helper.delete_product(product_delete_input)
        return DeleteProduct(product=product)


class ActivateProduct(graphene.Mutation):
    """
    Активация продукта клиента(выставление на аукцион)
    """

    class Arguments:
        product_id = graphene.ID(required=True)

    product = graphene.Field(ProductType)

    @login_required
    def mutate(self, info, product_id):
        client = info.context.user

        product_action_input = ProductActionInput(
            seller=client,
            product_id=product_id,
        )

        product = graphql_helper.activate_product(product_action_input)
        return DeleteProduct(product=product)


class CreateBid(graphene.Mutation):
    """
    Создание ставки на товар
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

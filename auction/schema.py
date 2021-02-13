import graphene

from auction.helpers.graphql import (
    get_product,
    get_product_list,
    get_product_price,
)
from auction.structures.graphql import IdInput, PageListInput

from .mutations import (
    ActivateProduct,
    CreateBid,
    CreateProduct,
    DeleteProduct,
    UpdateProduct,
)
from .types import ProductType


class Query(graphene.ObjectType):
    product_list = graphene.List(
        ProductType,
        page=graphene.Int(),
        page_size=graphene.Int(),
        description="Получаем список продуктов на аукционе",
    )

    product = graphene.Field(
        ProductType,
        id=graphene.ID(required=True),
        description="Получаем конкретный продукт",
    )
    product_price = graphene.Decimal(
        id=graphene.ID(required=True),
        description="Получаем цену конкретного продукта",
    )

    def resolve_product_list(
        self,
        info,
        page=1,
        page_size=10,
    ):
        """
        Получаем список продуктов на аукционе
        """
        input: PageListInput = PageListInput(page=page, page_size=page_size)
        return get_product_list(input=input)

    def resolve_product(self, info, id):
        """
        Получаем конкретный продукт
        """
        input: IdInput = IdInput(id=id)
        return get_product(input=input)

    def resolve_product_price(self, info, id):
        """
        Получаем цену продукта
        """
        input: IdInput = IdInput(id=id)
        return get_product_price(input=input)


class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    create_bid = CreateBid.Field()
    delete_product = DeleteProduct.Field()
    update_product = UpdateProduct.Field()
    activate_product = ActivateProduct.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)

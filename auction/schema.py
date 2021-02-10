import graphene
from django.core.paginator import Page

from auction.helpers.graphql import get_product_list
from auction.structures.graphql import PageListInput

from .models import Product
from .mutations import (ActivateProduct, CreateBid, CreateProduct,
                        DeleteProduct, UpdateProduct)
from .types import ProductType


class Query(graphene.ObjectType):
    product_list = graphene.List(
        ProductType, page=graphene.Int(), page_size=graphene.Int()
    )

    product = graphene.Field(ProductType, id=graphene.ID(required=True))
    product_price = graphene.Decimal(id=graphene.ID(required=True))

    def resolve_product_list(self, info, page=1, page_size=10):
        """
        получаем список продуктов на аукционе
        """
        input: PageListInput = PageListInput(page=page, page_size=page_size)
        return get_product_list(input=input)

    def resolve_product(self, info, id):
        """
        получаем конкретный продукт
        """
        return Product.objects.get(id=id)

    def resolve_product_price(self, info, id):
        """
        получаем цену продукта
        """
        price = Product.objects.get(id=id).get_final_bid_price()
        return price


class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    create_bid = CreateBid.Field()
    delete_product = DeleteProduct.Field()
    update_product = UpdateProduct.Field()
    activate_product = ActivateProduct.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)

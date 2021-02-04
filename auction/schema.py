import graphene
from django.core.paginator import Paginator

from .models import Product
from .mutations import CreateBid, CreateProduct, DeleteProduct, UpdateProduct
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
        products = Product.objects.all().order_by("id")
        paginator = Paginator(products, page_size)
        return paginator.page(page)

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
        print(price)
        return price


class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    create_bid = CreateBid.Field()
    delete_product = DeleteProduct.Field()
    update_product = UpdateProduct.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)

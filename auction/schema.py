import graphene
from django.core.paginator import Paginator
from .models import Client, Product
from .types import ClientType, ProductType
from .mutations import CreateProduct, CreateBid
from graphql_jwt.decorators import login_required


class Query(graphene.ObjectType):
    product_list = graphene.List(
        ProductType, page=graphene.Int(), page_size=graphene.Int()
    )

    product = graphene.Field(ProductType, id=graphene.ID(required=True))

    def resolve_product_list(self, info, page=1, page_size=10):
        """
        получаем список продуктов на аукционе
        """
        products = Product.objects.all()
        paginator = Paginator(products, page_size)
        return paginator.page(page)

    def resolve_product(self, info, id):
        """
        получаем конкретный продукт
        """
        return Product.objects.get(id=id)


class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    create_bid = CreateBid.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
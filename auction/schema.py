import graphene
from django.core.paginator import Paginator
from .models import Client, Product
from .types import ClientType, ProductType
from .mutations import CreateProduct
from graphql_jwt.decorators import login_required


class Query(graphene.ObjectType):
    product_list = graphene.List(
        ProductType, page=graphene.Int(), page_size=graphene.Int()
    )

    def resolve_product_list(self, info, page=1, page_size=10):
        products = Product.objects.all()
        paginator = Paginator(products, page_size)
        return paginator.page(page)


class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)

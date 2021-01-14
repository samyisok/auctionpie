import graphene
from auction.schema import schema as auction_schema


class Query(auction_schema.Query, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)
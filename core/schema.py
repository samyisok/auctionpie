import graphene
from auction.schema import schema as auction_schema


class Query(auction_schema.Query, graphene.ObjectType):
    pass


class Mutation(auction_schema.Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
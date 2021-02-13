import graphene
from graphql_auth import mutations
from graphql_auth.schema import MeQuery

from auction.schema import schema as auction_schema
from billing.schema import schema as billing_schema


class AuthMutation(graphene.ObjectType):
    register = mutations.Register.Field()
    verify_account = mutations.VerifyAccount.Field()

    # django-graphql-jwt inheritances
    token_auth = mutations.ObtainJSONWebToken.Field()
    verify_token = mutations.VerifyToken.Field()
    refresh_token = mutations.RefreshToken.Field()
    revoke_token = mutations.RevokeToken.Field()


class Query(
    auction_schema.Query,
    billing_schema.Query,
    MeQuery,
    graphene.ObjectType,
):
    pass


class Mutation(
    auction_schema.Mutation,
    # billing_schema.Mutation,
    AuthMutation,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)

import graphene
from graphql_auth import mutations
from graphql_auth.schema import MeQuery

from auction.schema import schema as auction_schema


class AuthMutation(graphene.ObjectType):
    register = mutations.Register.Field()
    verify_account = mutations.VerifyAccount.Field()
    # resend_activation_email = mutations.ResendActivationEmail.Field()
    # send_password_reset_email = mutations.SendPasswordResetEmail.Field()
    # password_reset = mutations.PasswordReset.Field()
    # password_change = mutations.PasswordChange.Field()

    # django-graphql-jwt inheritances
    token_auth = mutations.ObtainJSONWebToken.Field()
    verify_token = mutations.VerifyToken.Field()
    refresh_token = mutations.RefreshToken.Field()
    revoke_token = mutations.RevokeToken.Field()


class Query(auction_schema.Query, MeQuery, graphene.ObjectType):
    pass


class Mutation(auction_schema.Mutation, AuthMutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)

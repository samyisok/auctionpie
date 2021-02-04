from enum import Enum

from graphql import GraphQLError


class CoreError(Enum):
    UNEXPECTED_ERROR = "Unexpected Error"
    NO_CHANGES_SPECIFIED = "No changes specified"
    WRONG_USER = "Wrong user"

    def __init__(self, message: str) -> None:
        self.message = message

    @property
    def exception(self) -> GraphQLError:
        return GraphQLError(
            message=self.message, extensions={"code": self.name}
        )

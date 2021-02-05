from enum import Enum

from graphql import GraphQLError


class GenericException(GraphQLError):
    ...


class CodeError(Enum):
    UNEXPECTED_ERROR = "Unexpected Error"
    NO_CHANGES_SPECIFIED = "No changes specified"
    WRONG_USER = "Wrong user"

    def __init__(self, message: str) -> None:
        self.message = message

    @property
    def exception(self) -> GenericException:
        return GenericException(
            message=self.message, extensions={"code": self.code}
        )

    def __str__(self):
        """ Возвращаем мессадж по дефолту """
        return str(self.message)

    @property
    def code(self):
        return self.name

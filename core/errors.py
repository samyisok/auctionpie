from enum import Enum

from graphql import GraphQLError


class GenericException(GraphQLError):
    ...


class CodeError(Enum):
    UNEXPECTED_ERROR = "Unexpected Error"
    NO_CHANGES_SPECIFIED = "No changes specified"
    WRONG_USER = "Wrong user"
    NOT_FOUND_FINAL_BID = "Can not make a deal without bid and bidder"
    ALREADY_DELETED = "Already deleted"
    ALREADY_SOLDED = "Already solded"
    WRONG_TYPE = "Wrong type"
    ALREADY_HAS_HIGHER_BID = "Already has higher bid"
    AMOUNT_SHOULD_BE_POSITIVE = "Amount param should be postive"
    NOT_ENOUGH_BALANCE = "Not enough amount on balance"

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

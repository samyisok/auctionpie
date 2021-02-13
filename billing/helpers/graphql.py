"""
Методы для вызова из graphql
"""
from decimal import Decimal

from billing.models import Transaction
from billing.structures.graphql import ClientInput


def get_balance(input: ClientInput) -> Decimal:
    """
    получаем баланс клиента
    """
    return Transaction.balance(client=input.client)

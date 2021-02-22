"""
Методы для вызова из graphql
"""
from decimal import Decimal
from typing import Dict, List

from billing.models import Transaction
from billing.structures.graphql import ClientInput


def get_balance(input: ClientInput) -> Decimal:
    """
    получаем баланс клиента
    """
    return Transaction.balance(client=input.client)


# Платежные системы
def get_payment_systems(input: ClientInput) -> List[str]:
    """
    получаем платежные системы которые доступные для конкретного пользователя.
    например для юрлиц и бюджета должен быть доступен только банковский инвойс.
    """
    ...


def create_payment(input: ClientInput, payment_system: str, amount: str) -> int:
    """ создаем платеж для конкретного пользователя, получаем id платежа """
    ...


def get_payment(input: ClientInput, payment_id: int) -> Dict:
    """ возвращаем статус платежа и confirm_url """
    ...

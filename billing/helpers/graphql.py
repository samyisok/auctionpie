"""
Методы для вызова из graphql
"""
from decimal import Decimal
from typing import Dict, List

from django.core.exceptions import ObjectDoesNotExist

from billing.models import Payment, Transaction
from billing.structures.graphql import ClientInput, PaymentInfoInput
from core.errors import CodeError


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


def get_payment_info(input: PaymentInfoInput) -> Dict:
    """ возвращаем статус платежа и confirm_url """
    try:
        payment: Payment = Payment.objects.get(
            id=input.payment_id, client=input.client
        )
    except ObjectDoesNotExist:
        raise CodeError.PAYMENT_NOT_FOUND.exception

    return payment.get_payment_status_info()
    ...

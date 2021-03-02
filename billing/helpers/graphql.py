"""
Методы для вызова из graphql
"""
from decimal import Decimal
from typing import Dict, List, Union

from django.core.exceptions import ObjectDoesNotExist

from billing.models import Payment, Transaction
from billing.structures.graphql import (
    ClientInput,
    CreatePaymentInput,
    PaymentInfoInput,
)
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


def create_payment(input: CreatePaymentInput) -> int:
    """ создаем платеж для конкретного пользователя, получаем id платежа """
    payment: Payment = Payment.objects.create(
        client=input.client,
        expected_amount=input.amount,
        payment_system=input.payment_system,
        description="Предоплата",
    )

    payment.async_process()

    return payment.id


def get_payment_info(input: PaymentInfoInput) -> Dict[str, Union[str, bool]]:
    """ возвращаем статус платежа и confirm_url """
    try:
        payment: Payment = Payment.objects.get(
            id=input.payment_id, client=input.client
        )
    except ObjectDoesNotExist:
        raise CodeError.PAYMENT_NOT_FOUND.exception

    return payment.get_payment_status_info()

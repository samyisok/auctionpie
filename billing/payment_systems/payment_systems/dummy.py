from decimal import Decimal
from typing import TYPE_CHECKING

from billing.payment_systems.payment_system import (
    AbastactPaymentSystemResult,
    AbstractPaymentSystem,
    PaymentSystemResult,
)

if TYPE_CHECKING:
    from billing.models import Payment


class DummyPaymentSystem(AbstractPaymentSystem):
    """ Псевдо платежная система """

    def __init__(self, payment):
        self.payment: Payment = payment

    def process_payment(self) -> None:
        amount: Decimal = self.payment.expected_amount
        self.payment.set_payed(amount)

    def process_request(self) -> None:
        """ у Dummy нет внешнего сервиса для вызова реквеста """
        pass

    def get_process_payment_result(self) -> AbastactPaymentSystemResult:
        """
        Возвращаем обьект результатов обработки платежа
        так как возможно процесс платежа будет обрабатывать ассинхронно
        """

        return PaymentSystemResult(
            payment_system=self,
            invoice="",
            confirm_url="",
            failed=False,
            pending=False,
        )

    def is_process_payment_result_ready(self) -> bool:
        """
        Проверяем обработали ли платеж
        проверяем по наличию информации в платеже в поле data
        """
        return True

    @classmethod
    def is_confirm_avalible(cls) -> bool:
        """ Урл подвтерждения не доступен """
        return False

    @classmethod
    def is_invoice_avalible(cls) -> bool:
        """ инвойс не доступен """
        return False

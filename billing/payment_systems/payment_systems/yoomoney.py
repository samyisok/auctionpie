from typing import TYPE_CHECKING

from django.conf import settings
from yookassa import Configuration
from yookassa import Payment as YookassaPayment

from billing.payment_systems.payment_system import (
    AbastactPaymentSystemResult,
    AbstractPaymentSystem,
    PaymentSystemResult,
)

if TYPE_CHECKING:
    from yookassa.domain.response import (
        PaymentResponse as YoomoneyPaymentResponse,
    )

    from billing.models import Payment


YOOMONEY = settings.YOOMONEY
Configuration.account_id = settings.PAYMENT_SYSTEMS[YOOMONEY]["key"]
Configuration.secret_key = settings.PAYMENT_SYSTEMS[YOOMONEY]["shop_id"]


class YoomoneyPaymentSystem(AbstractPaymentSystem):
    """ Yoomoney платежная система """

    def __init__(self, payment):
        self.payment: Payment = payment

    def process_payment(self) -> None:
        payment: YoomoneyPaymentResponse = YookassaPayment.create(
            {
                "amount": {
                    "value": self.payment.expected_amount,
                    "currency": "RUB",
                },
                "payment_method_data": {"type": "bank_card"},
                "confirmation": {
                    "type": "redirect",
                    "return_url": settings.PAYMENT_SYSTEMS[YOOMONEY][
                        "return_url"
                    ],
                },
                "description": self.payment.description,
            }
        )

        self.payment.data = payment.json()
        self.payment.save()

    def process_request(self) -> None:
        """ нет внешнего сервиса для вызова реквеста """
        pass

    def get_process_payment_result(self) -> AbastactPaymentSystemResult:
        """
        Возвращаем обьект результатов обработки платежа
        так как возможно процесс платежа будет обрабатывать ассинхронно
        """

        # TODO вынести отдельно и наверно схему подрубить.
        json_data = self.payment.data
        pending = json_data["status"] == "pending"
        confirm_url = json_data["confirmation"]["return_url"]
        invoice = ""
        failed = False

        return PaymentSystemResult(
            payment_system=self,
            confirm_url=confirm_url,
            pending=pending,
            invoice=invoice,
            failed=failed,
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

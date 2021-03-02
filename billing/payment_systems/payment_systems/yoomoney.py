from __future__ import annotations

import json
from typing import TYPE_CHECKING, Dict, Union

from django.conf import settings
from yookassa import Configuration
from yookassa import Payment as YookassaPayment

from billing.payment_systems.payment_system import (
    AbastactPaymentSystemResult,
    AbstractPaymentSystem,
    PaymentSystemResult,
)

if TYPE_CHECKING:
    from billing.models import Payment
    from yookassa.domain.response import (
        PaymentResponse as YoomoneyPaymentResponse,
    )


YOOMONEY: str = settings.YOOMONEY
config_payment_systems: Dict[
    str, Dict[str, Union[str, bool, None]]
] = settings.PAYMENT_SYSTEMS
Configuration.account_id = config_payment_systems[YOOMONEY]["key"]
Configuration.secret_key = config_payment_systems[YOOMONEY]["shop_id"]
return_url = config_payment_systems[YOOMONEY]["return_url"]


class YoomoneyPaymentSystem(AbstractPaymentSystem):
    """ Yoomoney платежная система """

    def __init__(self, payment: Payment) -> None:
        self.payment: Payment = payment

    def process_payment(self) -> None:
        payment: YoomoneyPaymentResponse = YookassaPayment.create(
            {
                "amount": {
                    "value": self.payment.expected_amount,
                    "currency": "RUB",
                },
                "payment_method_data": {"type": "bank_card"},
                "confirmation": {"type": "redirect", "return_url": return_url},
                "description": self.payment.description,
            }
        )

        self.payment.data = json.loads(payment.json())
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
        success = json_data["status"] == "succeeded"

        return PaymentSystemResult(
            payment_system=self,
            confirm_url=confirm_url,
            pending=pending,
            invoice=invoice,
            failed=failed,
            success=success,
        )

    def is_process_payment_result_ready(self) -> bool:
        """
        Проверяем обработали ли платеж
        проверяем по наличию информации в платеже в поле data
        """
        return "status" in self.payment.data

    @classmethod
    def is_confirm_avalible(cls) -> bool:
        """ Урл подвтерждения доступен для этой платежной системы """
        return True

    @classmethod
    def is_invoice_avalible(cls) -> bool:
        """ инвойс не доступен """
        return False

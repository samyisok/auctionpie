from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from billing.models import Payment

from billing.meta import PaymentSystem
from billing.payment_systems.payment_system import AbstractPaymentSystem
from billing.payment_systems.payment_systems.dummy import DummyPaymentSystem


class PaymentSystemFactory:
    mapping = {PaymentSystem.DUMMY: DummyPaymentSystem}

    @classmethod
    def get_payment_system(cls, payment: Payment) -> AbstractPaymentSystem:
        payment_system_class = cls.mapping[Payment.payment_system]
        return payment_system_class(payment)

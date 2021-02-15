from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from billing.payment_systems.payment_system import AbstractPaymentSystem

from django.db import models
from django.utils import timezone

from auction.models import Client
from billing.meta import BillType, PaymentStatus, PaymentSystem
from billing.models import Bill
from billing.models.base import ModelAbstract
from billing.payment_systems.payment_system_factory import PaymentSystemFactory
from core.errors import CodeError


class Payment(ModelAbstract):
    """
    Платежные счета, например пополнение баланса
    """

    client = models.ForeignKey(
        Client,
        verbose_name="Владелец транзакции",
        on_delete=models.CASCADE,
    )
    order_id = models.UUIDField("Уникальный номер заказа", default=uuid.uuid4)
    status = models.CharField(
        "Статус платежа",
        choices=PaymentStatus.choices,
        max_length=32,
        default=PaymentStatus.NOT_PAYED,
    )
    payment_system = models.CharField(
        "Тип платежной системы",
        choices=PaymentSystem.choices,
        max_length=64,
        default=PaymentSystem.DUMMY,
    )
    expected_amount = models.DecimalField(
        "Ожидаймые средства", max_digits=19, decimal_places=2
    )
    amount = models.DecimalField(
        "Пришедшие средства",
        max_digits=19,
        decimal_places=2,
        default=Decimal(0),
    )
    payed_date = models.DateTimeField("Время оплаты", null=True)
    req_date = models.DateTimeField("Время оплаты", null=True)
    data = models.JSONField("Информация от платежной системы")
    bill = models.ForeignKey(
        "billing.Bill",
        verbose_name="Счет завершения оплаты",
        on_delete=models.CASCADE,
        null=True,
    )

    class Meta:
        indexes = [models.Index(fields=["order_id"])]

    def process_payment(self) -> None:
        """
        Начать обрабатывать платеж

        Цель обработки - отдать платеж в платежную систему
        и получить URL для продолжения платежа там где клиент оплатит

        Платеж переидет в статус pending, так как будет ждать пользователя.
        """
        payment_system: AbstractPaymentSystem = (
            PaymentSystemFactory.get_payment_system(self)
        )

        payment_system.process_payment()

    def process_request(self):
        """
        Обработать внешний реквест от платежной системы.

        Как правило в реквесте будет подтвеждение платежа.
        и далее подтвеждаем платеж или проверяем что платеж завершился ошибкой.
        """
        payment_system: AbstractPaymentSystem = (
            PaymentSystemFactory.get_payment_system(self)
        )

        payment_system.process_request()

    def set_payed(self, amount: Decimal) -> None:
        """
        Оплачиваем платеж

        Ставим статус то что платеж оплачен.
        Создаем счет на пополнение баланса.
        """
        if self.status not in [PaymentStatus.NOT_PAYED, PaymentStatus.PENDING]:
            raise CodeError.WRONG_STATUS.exception

        self.status = PaymentStatus.PAYED
        self.payed_date = timezone.now()
        self.amount = amount

        self.save()
        self.create_bill()

    def set_failed(self):
        """
        устанавливает статус failed когда получаем ошибку от ПС
        уведомляем пользователя
        """
        pass

    def set_cancelled(self):
        """
        устанавлиаем статус как cancelled
        """
        pass

    def create_bill(self) -> Bill:
        """
        создаем счет на пополнение баланса
        """
        bill: Bill = Bill.objects.create(
            client=self.client,
            bill_type=BillType.PREPAY,
            amount=self.amount,
            vat=self.client.vat,
        )

        bill.async_activate()

        return bill

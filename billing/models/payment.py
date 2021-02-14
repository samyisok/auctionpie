from __future__ import annotations

import uuid
from decimal import Decimal

from django.db import models

from auction.models import Client
from billing.models.base import ModelAbstract


class PaymentStatus(models.TextChoices):
    NOT_PAYED = "not_payed", "Не оплачен"
    PAYED = "payed", "Оплачен"
    PARTPAYED = "partpayed", "Частично оплачен"
    PENDING = "pending", "Ждем подтверждения оплаты"
    FAILED = "failed", "Оплата не успешна"
    CANCELLED = "cancelled", "Оплата отмененна"


class PaymentSystem(models.TextChoices):
    DUMMY = "dummy", "Псевдо платежная система"


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

    def process_payment(self):
        """
        Начать обрабатывать платеж

        Цель обработки - отдать платеж в платежную систему
        и получить URL для продолжения платежа там где клиент оптатит.

        Платеж переидет в статус pending, так как будет ждать пользователя.
        """
        pass

    def process_request(self):
        """
        Обработать внешний реквест от платежной системы.

        Как правило в реквесте будет подтвеждение платежа.
        и далее подтвеждаем платеж или проверяем что платеж завершился ошибкой.
        """
        pass

    def set_payed(self):
        """
        Оплачиваем платеж

        Ставим статус то что платеж оплачен.
        Создаем счет на пополнение баланса.
        """
        pass

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

    def create_bill(self):
        """
        создаем счет на пополнение баланса
        """
        pass

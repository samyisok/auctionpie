from __future__ import annotations

from django.db import models
from auction.models import Client
from django.utils import timezone
from billing.strategies import BillStrategyFactory
from billing.meta import BillStatus, BillType
from billing.models import Transaction


class ModelAbstract(models.Model):
    cdate = models.DateTimeField("Дата создания", default=timezone.now)
    mdate = models.DateTimeField(
        "Дата изменения",
        auto_now=True,
        auto_now_add=False,
    )

    class Meta:
        abstract = True


class Bill(ModelAbstract):
    """
    Счета

    Необходимо для того чтобы нести доп.информацию по балансу, зачем, почему, откуда.
    """

    client = models.ForeignKey(
        Client,
        verbose_name="Владелец счета",
        on_delete=models.CASCADE,
    )
    bill_type = models.CharField(
        "Тип счета", max_length=32, choices=BillType.choices
    )
    status = models.CharField(
        "статус счета",
        max_length=32,
        choices=BillStatus.choices,
        default=BillStatus.NOT_ACTIVATED,
    )
    amount = models.DecimalField("Сумма счета", max_digits=19, decimal_places=2)
    vat = models.IntegerField("НДС")

    def __str__(self):
        return f"#{self.id} {self.bill_type}: {self.amount}({self.client})({self.status})"

    def activate(self):
        """ Метод активации счета, в момент активации проводим транзакцию по балансу """
        strategy = BillStrategyFactory.get_strategy(self)
        return strategy.activate()

    def create_transaction_deposit(self):
        """ создание пополнение в балансе """
        return Transaction.deposit(
            client=self.client, bill=self, amount=self.amount
        )

    def create_transaction_expense(self):
        """ создание списание в балансе """
        return Transaction.expense(
            client=self.client, bill=self, amount=self.amount
        )
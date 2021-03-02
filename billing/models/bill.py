from __future__ import annotations

from typing import TYPE_CHECKING, Type

from django.apps import apps
from django.db import models

from auction.models import Client
from billing.meta import BillStatus, BillType
from billing.models.base import ModelAbstract
from billing.strategies import BillStrategyFactory
from billing.tasks import bill_activate

if TYPE_CHECKING:
    from billing.models import Transaction
    from billing.strategies import BillStrategy


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

    def __str__(self) -> str:
        return f"#{self.id} {self.bill_type}: {self.amount}({self.client})({self.status})"

    def activate(self) -> Bill:
        """ Метод активации счета, в момент активации проводим транзакцию по балансу """
        strategy: BillStrategy = BillStrategyFactory.get_strategy(self)
        return strategy.activate()

    def async_activate(self) -> None:
        """ асинхронная активация счета """
        bill_activate.delay(bill_id=self.id)

    def create_transaction_deposit(self) -> Transaction:
        """ создание пополнение в балансе """
        transaction: Type[Transaction] = apps.get_model(
            "billing", "Transaction"
        )
        return transaction.deposit(
            client=self.client, bill=self, amount=self.amount
        )

    def create_transaction_expense(self) -> Transaction:
        """ создание списание в балансе """
        transaction: Type[Transaction] = apps.get_model(
            "billing", "Transaction"
        )
        return transaction.expense(
            client=self.client, bill=self, amount=self.amount
        )

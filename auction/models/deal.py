from django.db import models
from auction.models import Client
from auction.models import Product
from auction.models.base import ModelAbstract
from billing.models import Bill


class Deal(ModelAbstract):
    """
    Фиксируем аукцион в сделках.

    на основе сделок формируем счета и движения по балансу
    и делаем связь между сделками и счетами.

    """

    product = models.ForeignKey(
        Product, verbose_name="Товар", on_delete=models.CASCADE
    )
    buyer = models.ForeignKey(
        Client, verbose_name="Покупатель", on_delete=models.CASCADE
    )
    amount = models.DecimalField(
        "Сумма сделки", max_digits=19, decimal_places=2
    )
    bills = models.ManyToManyField(Bill, through="DealBill")


class DealBill(ModelAbstract):
    """связь между сделками и счетами"""

    deal = models.ForeignKey(
        Deal, verbose_name="Сделка", on_delete=models.CASCADE
    )
    bill = models.ForeignKey(
        Bill, verbose_name="Счет", on_delete=models.CASCADE
    )

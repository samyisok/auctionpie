from __future__ import annotations

from django.db import models
from django.apps import apps
from .client import Client
from decimal import Decimal

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from auction.models import Bid, Deal

# from auction.models import Deal


class ProductException(Exception):
    pass


class ProductStatus(models.TextChoices):
    """
    Товары на аукцион

    statuses flow
    inactive->active->sold->canceled
    inactive->active->deleted || inactive->deleted
    """

    ACTIVE = "active", "Активный"
    INACTIVE = "inactive", "Не активный"
    DELETED = "deleted", "Удаленный"
    SOLD = "sold", "Проданный"  # Завершенный аукцион
    CANCELED = "canceled", "Отменен"


class Product(models.Model):
    """ Продукты или товары на аукционе """

    seller = models.ForeignKey(Client, on_delete=models.CASCADE)
    name = models.CharField(max_length=128, blank=False)
    description = models.TextField(blank=False)
    start_price = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        blank=False,
    )
    buy_price = models.DecimalField(
        max_digits=11, decimal_places=2, null=True, blank=True
    )
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        choices=ProductStatus.choices,
        default=ProductStatus.INACTIVE,
        max_length=64,
    )
    cdate = models.DateTimeField(auto_now=False, auto_now_add=True)
    mdate = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.name

    def get_final_bid(self) -> Bid:
        """
        Получаем максимальный бид
        """

        where = models.Q(product=self)

        final_bid = self.bid_set.filter(where).order_by("-price").first()

        return final_bid

    def get_final_bid_price(self) -> Decimal:
        """
        Получаем максимальный бид или start_price этого продукта
        """

        final_bid: Bid = self.get_final_bid()

        if final_bid is None:
            return self.start_price

        return final_bid.price

    def make_a_deal(self) -> Deal:
        """
        Создание финализируещей сделки
        """
        final_bid: Bid = self.get_final_bid()

        if final_bid is None:
            raise ProductException("can not make a deal without bid and bidder")

        final_price: Decimal = final_bid.price

        deal_model = apps.get_model("auction", "Deal")
        deal: Deal = deal_model.objects.create(
            product=self, buyer=final_bid.client, amount=final_price
        )

        return deal

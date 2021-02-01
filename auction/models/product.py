from __future__ import annotations

from auction.tasks import product_send_email

import logging
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .client import Client

if TYPE_CHECKING:
    from auction.models import Bid, Deal


logger = logging.getLogger(__name__)


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
    start_date = models.DateTimeField(blank=True, null=False)
    end_date = models.DateTimeField(blank=True, null=False)
    status = models.CharField(
        choices=ProductStatus.choices,
        default=ProductStatus.INACTIVE,
        max_length=64,
    )
    cdate = models.DateTimeField(auto_now=False, auto_now_add=True)
    mdate = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.name

    def clean(self):
        """ валидация полей """

        active_statuses = [
            ProductStatus.ACTIVE,
            ProductStatus.SOLD,
            ProductStatus.CANCELED,
        ]

        if self.status in active_statuses and (
            self.start_date is None or self.end_date is None
        ):
            raise ValidationError("start_date and end_date should be defined")

        return super().clean()

    def save(self, *args, **kwargs):
        """ проверки перед сохранением товара"""
        self.full_clean()
        return super().save(*args, **kwargs)

    def get_final_bid(self) -> Optional[Bid]:
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

        final_bid: Optional[Bid] = self.get_final_bid()

        if final_bid is None:
            return self.start_price

        return final_bid.price

    def make_a_deal(self) -> Deal:
        """
        Создание финализируещей сделки
        """
        final_bid: Optional[Bid] = self.get_final_bid()

        if final_bid is None:
            raise ProductException("can not make a deal without bid and bidder")

        final_price: Decimal = final_bid.price

        deal_model = apps.get_model("auction", "Deal")
        deal: Deal = deal_model.objects.create(
            product=self, buyer=final_bid.client, amount=final_price
        )

        return deal

    def is_buy_condition_meet(self) -> bool:
        """
        проверяем условия закрытия сделки по цене.
        если покупная цена не указанна то возвращаем False
        если цена ставки польше покупной цены возвращаем True
        """

        if self.buy_price is None:
            return False

        final_price: Decimal = self.get_final_bid_price()
        buy_price: Decimal = self.buy_price

        return final_price >= buy_price

    def is_time_condition_meet(self) -> bool:
        """
        проверяем условия закрытия сделки по времени.
        чтобы закрыть сделку, текущее время должно больше end_date
        """
        if self.end_date is None:
            return False

        return self.end_date <= timezone.now()

    def is_ready_to_make_a_deal(self) -> bool:
        """
        проверяем множественные условия закрытия сделки.
        """
        # неактивные продукты не можем закрывать.
        if self.status is not ProductStatus.ACTIVE:
            return False

        # должна быть хоть одна ставка
        if self.get_final_bid() is None:
            return False

        return self.is_buy_condition_meet() or self.is_time_condition_meet()

    def bid_posthook(self) -> None:
        """
        Метод который дергаем из Bid после создании инстанса bid
        """
        logger.info(f"attemp make a deal for {self}")

        if self.is_ready_to_make_a_deal():
            deal: Deal = self.make_a_deal()
            logger.info(f"make a deal {deal}")

    def send_email(self, type: str):
        if type == "new":
            client: Client = self.seller
            return client.email_user(subject="new product", message=str(self))

    def async_send_email(self) -> None:
        product_send_email.delay(product_id=self.id, type="new")

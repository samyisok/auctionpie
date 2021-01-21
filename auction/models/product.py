from django.db import models
from .client import Client
from decimal import Decimal


class Product(models.Model):
    """
    Товары на аукцион

    statuses flow
    inactive->active->sold->canceled
    inactive->active->deleted || inactive->deleted
    """

    STATUSES = [
        ("active", "Активный"),
        ("inactive", "Неактивный"),
        ("deleted", "Удаленный"),
        ("sold", "Проданный"),
        ("canceled", "Отменен"),
    ]

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
        choices=STATUSES,
        default="inactive",
        max_length=64,
    )
    cdate = models.DateTimeField(auto_now=False, auto_now_add=True)
    mdate = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.name

    def get_final_bid_price(self) -> Decimal:
        """
        Получаем максимальный бид или start_price этого продукта
        """

        where = models.Q(product=self)

        final_price = (
            self.bid_set.filter(where)
            .order_by("-cdate")
            .values("price")
            .first()
        )

        if final_price is None:
            return self.start_price

        return final_price["price"]

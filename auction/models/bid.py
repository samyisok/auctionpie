from django.db import models

from .client import Client
from .product import Product


class BidStatus(models.TextChoices):
    ACTIVE = "active", "Активная ставка"
    DELETED = "deleted", "Удаленная ставка"


class Bid(models.Model):
    """ Ставки на товары """

    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, blank=False, null=False
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, blank=False, null=False
    )
    status = models.CharField(
        choices=BidStatus.choices,
        default=BidStatus.ACTIVE,
        max_length=32,
    )
    price = models.DecimalField(max_digits=19, decimal_places=2)
    cdate = models.DateTimeField(auto_now=False, auto_now_add=True)
    mdate = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return f"{self.product.name}: {self.price}"

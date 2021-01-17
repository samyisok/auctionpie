from django.db import models
from .client import Client
from .product import Product


class Bid(models.Model):
    STATUSES = [
        ("active", "Active"),
        ("deleted", "Deleted"),
    ]

    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, blank=False, null=False
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, blank=False, null=False
    )
    status = models.CharField(
        choices=STATUSES,
        default="active",
        max_length=32,
    )
    price = models.DecimalField(max_digits=11, decimal_places=2)
    cdate = models.DateTimeField(auto_now=False, auto_now_add=True)
    mdate = models.DateTimeField(auto_now=True, auto_now_add=False)

from django.db import models
from .client import Client


class Product(models.Model):
    # statuses flow
    # inactive->active->sold->canceled
    # inactive->active->deleted || inactive->deleted
    STATUSES = [
        ("active", u"Активный"),
        ("inactive", u"Неактивный"),
        ("deleted", u"Удаленный"),
        ("sold", u"Проданный"),
        ("canceled", u"Отменен"),
    ]

    seller = models.ForeignKey(Client, on_delete=models.CASCADE)
    name = models.CharField(max_length=128, blank=False)
    description = models.TextField()
    start_price = models.DecimalField(max_digits=11, decimal_places=2, blank=False)
    buy_price = models.DecimalField(max_digits=11, decimal_places=2)
    start_date = models.TimeField(auto_now=False, auto_now_add=False)
    end_date = models.TimeField(auto_now=False, auto_now_add=False)
    status = models.CharField(choices=STATUSES, default="inactive", max_length=64)
    cdate = models.TimeField(auto_now=False, auto_now_add=True)
    mdate = models.TimeField(auto_now=True, auto_now_add=False)

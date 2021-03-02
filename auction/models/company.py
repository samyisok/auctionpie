from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    inn = models.CharField(max_length=10)
    vat = models.IntegerField("НДС")
    is_vat_active = models.BooleanField("Включен НДС")
    cdate = models.DateTimeField(auto_now=False, auto_now_add=True)
    mdate = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self) -> str:
        return self.name

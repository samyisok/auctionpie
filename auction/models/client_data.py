from django.db import models

from .client import Client


class ClientData(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=128)
    middle_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    company_name = models.CharField(max_length=128)
    inn = models.CharField(max_length=50)
    kpp = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=50)
    account_number = models.CharField(max_length=50)
    bik = models.CharField(max_length=50)
    real_address = models.CharField(max_length=50)
    billing_address = models.CharField(max_length=128)
    cdate = models.DateTimeField(auto_now=False, auto_now_add=True)
    mdate = models.DateTimeField(auto_now=True, auto_now_add=False)

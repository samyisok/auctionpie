from django.contrib import admin
from billing.models import Transaction, Bill

# Register your models here.
admin.site.register(Transaction)
admin.site.register(Bill)

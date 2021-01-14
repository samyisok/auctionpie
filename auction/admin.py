from django.contrib import admin
from auction.models import Client, ClientData, Product

admin.site.register(Client)
admin.site.register(ClientData)
admin.site.register(Product)
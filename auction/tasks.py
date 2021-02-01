from celery import shared_task
from django.apps import apps


@shared_task
def product_send_email(product_id, type):
    product_model = apps.get_model("auction", "Product")
    product = product_model.objects.get(id=product_id)
    return product.send_email(type)

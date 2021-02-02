from celery import shared_task
from django.apps import apps


@shared_task
def product_send_email(product_id, type):
    """ посылаем письмо клиенту по продукту """
    product_model = apps.get_model("auction", "Product")
    product = product_model.objects.get(id=product_id)
    return product.send_email(type)


@shared_task
def deal_send_email(deal_id, type):
    """ посылаем письмо клиенту по сделки """
    pass


@shared_task
def deal_finalize(deal_id):
    """ финализируем сделку """
    deal_model = apps.get_model("auction", "Deal")
    deal = deal_model.objects.get(id=deal_id)
    return deal.finalize()

import logging
from typing import TYPE_CHECKING

from django.apps import apps

from core.celery import app

if TYPE_CHECKING:
    from auction.models import Product

logger = logging.getLogger(__name__)


@app.task()
def product_send_email(product_id: int, type: str) -> None:
    """ посылаем письмо клиенту по продукту """
    product_model = apps.get_model("auction", "Product")
    product: Product = product_model.objects.get(id=product_id)
    product.send_email(type)


@app.task()
def deal_send_email(deal_id, type):
    """ посылаем письмо клиенту по сделки """
    pass


@app.task()
def deal_finalize(deal_id):
    """ финализируем сделку """
    deal_model = apps.get_model("auction", "Deal")
    deal = deal_model.objects.get(id=deal_id)
    return deal.finalize()


@app.task(bind=True, max_retries=1200)
def product_try_to_make_a_deal(self, product_id):
    try:
        product_model = apps.get_model("auction", "Product")
        product: Product = product_model.objects.get(id=product_id)
        if product.is_ready_to_make_a_deal():
            product.make_a_deal()
        else:
            raise Exception("Product not ready yet")
    except Exception as exc:
        logger.warning(f"Failed make a deal: {exc}")
        raise self.retry(exc=exc, countdown=5)

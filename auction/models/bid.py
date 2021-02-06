import logging
from decimal import Decimal

from django.db import models

from auction.models.client import Client
from auction.models.product import Product
from core.errors import CodeError

logger = logging.getLogger(__name__)


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

    class Meta:
        indexes = [models.Index(fields=["price"])]

    def __str__(self):
        return f"{self.product.name}: {self.price}"

    @classmethod
    def is_possible_to_place_bid(cls, product: Product, price: Decimal) -> bool:
        """ Проверки возможности установки ставки перед сохранением """

        where = models.Q(product=product, price__gte=price)

        bid = cls.objects.filter(where).first()

        return bid is None

    def clean(self):
        super().clean()
        if not Bid.is_possible_to_place_bid(
            product=self.product, price=self.price
        ):
            raise CodeError.ALREADY_HAS_HIGHER_BID.exception

    def save(self, *args, **kwargs):
        """ проверки перед сохранением ставки """
        self.full_clean()
        return super().save(*args, **kwargs)

    def post_save(self):
        """ будем вызывать из хелпера отдельно """
        try:
            self.product.bid_posthook()
        except Exception as e:
            logger.warning(f"failed posthook: {e}")

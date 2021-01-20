from django.test import TestCase
from auction.models import Client, Product, Bid
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta


email = "emailfortest@test.ru"
email_seller = "seller@test.ru"
amount = Decimal("12.34")
product_params = {
    "name": "product name",
    "description": "product desc",
    "start_price": Decimal(10),
    "buy_price": Decimal(20),
    "start_date": timezone.now(),
    "end_date": timezone.now() + timedelta(7),
}


class ModelsProductGetFinalBidPriceTestCase(TestCase):
    """get final bid price"""

    def setUp(self):
        self.client = Client.objects.create_user(email, "password")
        self.seller = Client.objects.create_user(email_seller, "password")
        self.product_params = {"seller": self.seller, **product_params}
        self.product = Product.objects.create(**self.product_params)

    def test_get_final_bid_price_should_return_start_price(self):
        """should return start price"""
        final_price = self.product.get_final_bid_price()
        self.assertEqual(final_price, product_params["start_price"])

    def test_get_final_bid_price_should_return_final_bid_price(self):
        """should return bid price"""
        Bid.objects.create(
            client=self.client, product=self.product, price=amount
        )
        Bid.objects.create(
            client=self.client, product=self.product, price=amount + 1
        )

        final_price = self.product.get_final_bid_price()
        self.assertEqual(final_price, amount + 1)

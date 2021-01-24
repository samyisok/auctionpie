from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from auction.models import Bid, Client, Deal, Product
from auction.models.product import ProductException

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

    def test_get_final_bid(self):
        """ should return funal bid """
        Bid.objects.create(
            client=self.client, product=self.product, price=amount
        )
        bid2 = Bid.objects.create(
            client=self.client, product=self.product, price=amount + 1
        )
        Bid.objects.create(
            client=self.client, product=self.product, price=amount
        )

        final_bid = self.product.get_final_bid()

        self.assertIsInstance(final_bid, Bid)
        self.assertEqual(final_bid.id, bid2.id)

    def test_get_final_bid_none(self):
        """ should do not find final bid """
        final_bid = self.product.get_final_bid()

        self.assertIsNone(final_bid)

    def test_make_a_deal_exception(self):
        """ product should raise exception when bid is None """
        with self.assertRaisesMessage(
            ProductException, "can not make a deal without bid and bidder"
        ):
            self.product.make_a_deal()

    def test_make_a_deal(self):
        """ should create a deal """

        Bid.objects.create(
            client=self.client, product=self.product, price=amount
        )

        deal = self.product.make_a_deal()

        deal_from_db = self.product.deal

        self.assertIsInstance(deal, Deal)
        self.assertEqual(deal.id, deal_from_db.id)

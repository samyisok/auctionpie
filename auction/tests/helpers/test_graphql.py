from django.test import TestCase
from auction.models import Client, Product, Bid
from decimal import Decimal
from auction.helpers import graphql as graphql_helper
from auction.structures.graphql import BidInput, ProductInput
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


class HelperGraphqlCreateBidTestCase(TestCase):
    """Create bid"""

    def setUp(self):
        self.client = Client.objects.create_user(email, "password")
        self.seller = Client.objects.create_user(email_seller, "password")
        self.product_params = {"seller": self.seller, **product_params}
        self.product = Product.objects.create(**self.product_params)

    def test_create_bid_success(self):
        "should be success"
        bid_input = BidInput(
            client=self.client, price=amount, product_id=self.product.id
        )

        bid = graphql_helper.create_bid(bid_input=bid_input)

        self.assertIsNotNone(bid)
        self.assertIsInstance(bid, Bid)
        self.assertEqual(bid.price, amount)


class HelperGraphqlCreateProductTestCase(TestCase):
    """Create product"""

    def setUp(self):
        self.seller = Client.objects.create_user(email_seller, "password")
        self.product_params = {"seller": self.seller, **product_params}

    def test_create_product_success(self):
        product_input = ProductInput(**self.product_params)

        product = graphql_helper.create_new_product(product_input)

        product_attributes = {
            k: product.__dict__[k] for k in product_params.keys()
        }

        self.assertIsNotNone(product)
        self.assertIsInstance(product, Product)
        self.assertDictEqual(product_attributes, product_params)
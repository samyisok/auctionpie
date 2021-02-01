from datetime import timedelta
from decimal import Decimal
from unittest import mock

from django.test import TestCase
from django.utils import timezone

from auction.helpers import graphql as graphql_helper
from auction.models import Bid, Client, Product
from auction.structures.graphql import BidInput, ProductInput

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

    @mock.patch("auction.models.Bid.post_save", return_value=True)
    def test_create_bid_success(self, mock_post_save):
        "should be success"
        bid_input = BidInput(
            client=self.client, price=amount, product_id=self.product.id
        )

        bid = graphql_helper.create_bid(bid_input=bid_input)

        self.assertIsNotNone(bid)
        self.assertIsInstance(bid, Bid)
        self.assertEqual(bid.price, amount)
        mock_post_save.assert_called_once_with()


class HelperGraphqlCreateProductTestCase(TestCase):
    """Create product"""

    def setUp(self):
        self.seller = Client.objects.create_user(email_seller, "password")
        self.product_params = {"seller": self.seller, **product_params}

    @mock.patch("auction.models.Product.async_send_email")
    def test_create_product_success(self, mock_async_send_email):
        product_input = ProductInput(**self.product_params)

        product = graphql_helper.create_new_product(product_input)

        product_attributes = {
            k: product.__dict__[k] for k in product_params.keys()
        }

        self.assertIsNotNone(product)
        self.assertIsInstance(product, Product)
        self.assertDictEqual(product_attributes, product_params)
        mock_async_send_email.assert_called_once_with(type="new")

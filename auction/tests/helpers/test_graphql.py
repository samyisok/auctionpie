from datetime import timedelta
from decimal import Decimal
from unittest import mock

from django.test import TestCase
from django.utils import timezone

from auction.helpers import graphql as graphql_helper
from auction.models import Bid, Client, Product
from auction.models.product import ProductStatus
from auction.structures.graphql import (BidInput, ProductDeleteInput,
                                        ProductInput, ProductUpdateInput)
from core.errors import CodeError, GenericException

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


class HelperGraphqlDeleteProductTestCase(TestCase):
    """ Delete product """

    def setUp(self):
        self.seller = Client.objects.create_user(email_seller, "password")
        self.product_params = {"seller": self.seller, **product_params}
        self.product = Product.objects.create(**self.product_params)

    def test_delete_product_success(self):
        """ should change status to deleted """
        product_delete_input = ProductDeleteInput(
            product_id=self.product.id, seller=self.seller
        )

        product = graphql_helper.delete_product(
            product_delete_input=product_delete_input
        )

        self.assertIsNotNone(product)
        self.assertIsInstance(product, Product)
        self.assertEqual(product.status, ProductStatus.DELETED)

    def test_delete_product_should_raise_exception(self):
        """ should raise exception if wrong user """
        another_client: Client = Client.objects.create_user(
            "another_client@another.com", "password"
        )

        product_delete_input = ProductDeleteInput(
            product_id=self.product.id, seller=another_client
        )

        with self.assertRaisesMessage(
            GenericException, CodeError.WRONG_CLIENT.message
        ):
            graphql_helper.delete_product(
                product_delete_input=product_delete_input
            )


class HelperGraphqlUpdateProductTestCase(TestCase):
    """ Update product """

    def setUp(self):
        self.seller = Client.objects.create_user(email_seller, "password")
        self.product_params = {"seller": self.seller, **product_params}
        self.product = Product.objects.create(**self.product_params)

    def test_update_product_success(self):
        """ update all fields """
        new_product_params = {
            "name": "new product name",
            "description": "new product desc",
            "start_price": Decimal(99),
            "buy_price": Decimal(199),
            "start_date": timezone.now() + timedelta(10),
            "end_date": timezone.now() + timedelta(20),
        }

        product_update_input = ProductUpdateInput(
            product_id=self.product.id, seller=self.seller, **new_product_params
        )

        product = graphql_helper.update_product(product_update_input)

        updated_product_attributes = {
            k: product.__dict__[k] for k in new_product_params.keys()
        }

        self.assertIsNotNone(product)
        self.assertIsInstance(product, Product)

        self.assertDictEqual(updated_product_attributes, new_product_params)

    def test_update_product_success_only_desc(self):
        """ update only desc field """
        new_product_params = {
            "description": "new product desc",
        }

        product_update_input = ProductUpdateInput(
            product_id=self.product.id, seller=self.seller, **new_product_params
        )

        product = graphql_helper.update_product(product_update_input)
        self.assertIsNotNone(product)
        self.assertIsInstance(product, Product)
        self.assertEqual(product.description, new_product_params["description"])
        self.assertEqual(product.name, product_params["name"])

    def test_update_product_raise_wrong_client(self):
        """ update raise error wrong user"""
        new_product_params = {
            "description": "new product desc",
        }

        second_seller = Client.objects.create_user(
            "second_seller@test.com", "password"
        )

        product_update_input = ProductUpdateInput(
            product_id=self.product.id,
            seller=second_seller,
            **new_product_params,
        )

        with self.assertRaisesMessage(
            GenericException, CodeError.WRONG_CLIENT.message
        ):
            graphql_helper.update_product(product_update_input)

    def test_update_product_raise_no_changes(self):
        """ update raise error no changes"""
        new_product_params = {}

        product_update_input = ProductUpdateInput(
            product_id=self.product.id, seller=self.seller, **new_product_params
        )

        with self.assertRaisesMessage(
            GenericException, CodeError.NO_CHANGES_SPECIFIED.message
        ):
            graphql_helper.update_product(product_update_input)

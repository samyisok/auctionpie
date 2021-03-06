from unittest import mock

from django.test import TestCase

from auction.models import Bid, Client, Product
from auction.tests.fixtures import (
    amount,
    email,
    email_seller,
    password,
    password_seller,
    product_params,
)
from core.errors import CodeError, GenericException


class ModelsBidTestCase(TestCase):
    """bid test"""

    def setUp(self):
        self.client = Client.objects.create_user(email, password)
        self.seller = Client.objects.create_user(email_seller, password_seller)
        self.product_params = {"seller": self.seller, **product_params}
        self.product = Product.objects.create(**self.product_params)
        self.first_bid = Bid.objects.create(
            client=self.client, product=self.product, price=amount
        )

    def test_str(self):
        """ Должен отдавать нормальную строку """
        self.assertEqual(str(self.first_bid), "product name: 12.34")

    def test_is_possible_to_place_bid_true(self):
        """ should return true if price is higher """
        result = Bid.is_possible_to_place_bid(
            product=self.product, price=amount + 1
        )
        self.assertEqual(result, True)

    def test_is_possible_to_place_bid_false(self):
        """ should return false if price is lower """
        result = Bid.is_possible_to_place_bid(
            product=self.product, price=amount - 1
        )
        self.assertEqual(result, False)

    def test_is_possible_to_place_bid_false_eq(self):
        """ should return false if price is equal """
        result = Bid.is_possible_to_place_bid(
            product=self.product, price=amount
        )
        self.assertEqual(result, False)

    def test_is_possible_to_place_bid_true_another_product(self):
        """ should return true if another clean product """
        self.product.id = None
        self.product.save()

        result = Bid.is_possible_to_place_bid(
            product=self.product, price=amount - 1
        )
        self.assertEqual(result, True)

    def test_save_exception(self):
        """
        should raise a exception when create a bid
        with lower or equal amount of price than other bids for this product
        """
        with self.assertRaisesMessage(
            GenericException, CodeError.ALREADY_HAS_HIGHER_BID.message
        ):
            Bid.objects.create(
                client=self.client, product=self.product, price=amount - 1
            )

        with self.assertRaisesMessage(
            GenericException, CodeError.ALREADY_HAS_HIGHER_BID.message
        ):
            Bid.objects.create(
                client=self.client, product=self.product, price=amount
            )

    @mock.patch("auction.models.Product.bid_posthook", return_value=True)
    def test_post_save(self, mock_bid_posthook):
        """ should call bid posthook from product """
        self.first_bid.post_save()
        mock_bid_posthook.assert_called_once_with()

    @mock.patch("auction.models.Product.bid_posthook")
    def test_post_save_should_rise(self, mock_bid_posthook):
        """ should rise exception """
        log_msg = "WARNING:auction.models.bid:failed posthook: Test Exception"

        mock_bid_posthook.side_effect = Exception("Test Exception")

        with self.assertLogs("auction.models.bid") as mock_log:
            self.first_bid.post_save()
            self.assertEqual(mock_log.output, [log_msg])

from datetime import timedelta
from decimal import Decimal
from typing import Dict
from unittest import mock

from django.test import TestCase
from django.utils import timezone

from auction.models import Bid, Client, Deal, Product
from auction.models.product import ProductException, ProductStatus

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


class ModelsProductTestCase(TestCase):
    """product model test"""

    def setUp(self):
        self.client: Client = Client.objects.create_user(email, "password")
        self.seller: Client = Client.objects.create_user(
            email_seller, "password"
        )
        self.product_params: Dict = {"seller": self.seller, **product_params}
        self.product: Product = Product.objects.create(**self.product_params)

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

    def test_is_buy_condition_meet_true(self):
        """ should return true """
        Bid.objects.create(
            client=self.client, product=self.product, price=Decimal(20)
        )
        self.assertTrue(self.product.is_buy_condition_meet())

    def test_is_buy_condition_meet_false(self):
        """ should return false """
        Bid.objects.create(
            client=self.client, product=self.product, price=Decimal(15)
        )
        self.assertFalse(self.product.is_buy_condition_meet())

    def test_is_buy_condition_meet_false_buy_price_none(self):
        """ should return false if buy_price is not defined """
        self.product.id = None
        self.product.buy_price = None
        self.product.save()
        Bid.objects.create(
            client=self.client, product=self.product, price=Decimal(20)
        )

        self.assertFalse(self.product.is_buy_condition_meet())

    def test_is_time_condition_meet_true(self):
        """ should return true """
        self.product.end_date = timezone.now()
        self.product.save()
        self.assertTrue(self.product.is_time_condition_meet())

        self.product.end_date = timezone.now() - timedelta(1)
        self.product.save()
        self.assertTrue(self.product.is_time_condition_meet())

    def test_is_time_condition_meet_false(self):
        """ should return false """
        self.product.end_date = timezone.now() + timedelta(1)
        self.product.save()
        self.assertFalse(self.product.is_time_condition_meet())

    def test_is_time_condition_meet_false_end_date(self):
        """ should return false if end date not defined """
        self.product.end_date = None
        self.product.save()
        self.assertFalse(self.product.is_time_condition_meet())

    def test_is_ready_to_make_a_deal_status_false(self):
        """ should return false if status not Actve """
        self.assertFalse(self.product.is_ready_to_make_a_deal())

    @mock.patch("auction.models.Product.get_final_bid", return_value=None)
    def test_is_ready_to_make_a_deal_not_bidded_false(self, mock_get_final_bid):
        """ should return false if product not have any bids """
        self.product.status = ProductStatus.ACTIVE
        self.product.save()
        self.assertFalse(self.product.is_ready_to_make_a_deal())
        mock_get_final_bid.assert_called_once_with()

    def test_is_ready_to_make_a_deal_raise_exception(self):
        """ should return raise exception if end_date not defined """
        self.product.end_date = None
        self.product.status = ProductStatus.ACTIVE
        self.product.save()
        Bid.objects.create(
            client=self.client, product=self.product, price=Decimal(20)
        )

        with self.assertRaisesMessage(ProductException, "invalid product"):
            self.product.is_ready_to_make_a_deal()

    @mock.patch(
        "auction.models.Product.is_buy_condition_meet", return_value=False
    )
    @mock.patch(
        "auction.models.Product.is_time_condition_meet", return_value=True
    )
    def test_is_ready_to_make_a_deal_call_buy_condition(
        self, mock_time_cond, mock_buy_cond
    ):
        """ should call is_buy_condition_meet """
        self.product.status = ProductStatus.ACTIVE
        self.product.save()
        Bid.objects.create(
            client=self.client, product=self.product, price=Decimal(20)
        )

        self.assertTrue(self.product.is_ready_to_make_a_deal())
        mock_buy_cond.assert_called_once_with()
        mock_time_cond.assert_called_once_with()

    @mock.patch(
        "auction.models.Product.is_buy_condition_meet", return_value=True
    )
    @mock.patch(
        "auction.models.Product.is_time_condition_meet", return_value=False
    )
    def test_is_ready_to_make_a_deal_call_time_condition(
        self, mock_time_condition, mock_buy_condition
    ):
        """ should call is_buy_condition_meet """
        self.product.status = ProductStatus.ACTIVE
        self.product.save()
        Bid.objects.create(
            client=self.client, product=self.product, price=Decimal(20)
        )

        self.assertTrue(self.product.is_ready_to_make_a_deal())
        mock_buy_condition.assert_called_once_with()
        mock_time_condition.assert_not_called()

    @mock.patch(
        "auction.models.Product.is_ready_to_make_a_deal", return_value=True
    )
    @mock.patch(
        "auction.models.Product.make_a_deal",
    )
    def test_bid_posthook(self, mock_a_deal, mock_is_ready):
        """ should call make_a_deal """
        deal = mock.Mock(spec=Deal)
        mock_a_deal.return_value = deal

        log_msg1 = (
            f"INFO:auction.models.product:attemp make a deal for {self.product}"
        )
        log_msg2 = f"INFO:auction.models.product:make a deal {deal}"

        with self.assertLogs(
            "auction.models.product", level="INFO"
        ) as mock_log:
            self.product.bid_posthook()
            mock_is_ready.assert_called_once_with()
            self.assertEqual(mock_log.output, [log_msg1, log_msg2])

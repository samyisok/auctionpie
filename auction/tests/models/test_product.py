from datetime import timedelta
from decimal import Decimal
from typing import Dict
from unittest import mock

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from auction.models import Bid, Client, Deal, Product
from auction.models.product import ProductStatus
from auction.tests.fixtures import (
    amount,
    email,
    email_seller,
    password,
    password_seller,
    product_params,
)
from core.errors import CodeError, GenericException


class ModelsProductTestCase(TestCase):
    """product model test"""

    def setUp(self):
        self.client: Client = Client.objects.create_user(email, password)
        self.seller: Client = Client.objects.create_user(
            email_seller, password_seller
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
            GenericException, "Can not make a deal without bid and bidder"
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
        deal.async_finalize = mock.Mock()
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
            mock_a_deal.assert_called_once_with()
            deal.async_finalize.assert_called_once_with()
            self.assertEqual(mock_log.output, [log_msg1, log_msg2])

    @mock.patch(
        "auction.models.Product.is_ready_to_make_a_deal", return_value=False
    )
    @mock.patch(
        "auction.models.Product.make_a_deal",
    )
    def test_bid_posthook_not_ready_make_deal(self, mock_a_deal, mock_is_ready):
        """ should does not call make_a_deal """
        deal = mock.Mock(spec=Deal)
        deal.async_finalize = mock.Mock()
        mock_a_deal.return_value = deal

        log_msg1 = (
            f"INFO:auction.models.product:attemp make a deal for {self.product}"
        )

        with self.assertLogs(
            "auction.models.product", level="INFO"
        ) as mock_log:
            self.product.bid_posthook()
            mock_is_ready.assert_called_once_with()
            mock_a_deal.assert_not_called()
            deal.async_finalize.assert_not_called()
            self.assertEqual(mock_log.output, [log_msg1])

    def test_clean_raise_exception_active(self):
        """ should return raise exception if end_date not defined """

        list_of_statuses = [
            ProductStatus.ACTIVE,
            ProductStatus.SOLD,
            ProductStatus.CANCELED,
        ]

        for status in list_of_statuses:
            self.product.end_date = None
            self.product.status = status

            with self.assertRaisesMessage(
                ValidationError, "start_date and end_date should be defined"
            ):
                self.product.clean()

    @mock.patch(
        "auction.models.Product.full_clean",
    )
    def test_save(self, mock_full_clean):
        """ should call full_clean """
        self.product.id = None
        self.product.save()
        mock_full_clean.assert_called_once_with()

    @mock.patch(
        "auction.models.Client.email_user",
    )
    def test_send_email_new(self, mock_email_user):
        """ should call email user if type new """
        self.product.send_email(type="new")
        mock_email_user.assert_called_once_with(
            subject="new product",
            message=str(self.product),
        )

    def test_send_email_raise_exception(self):
        """ should raise exception if type is other"""
        with self.assertRaisesMessage(
            GenericException, CodeError.WRONG_TYPE.message
        ):
            self.product.send_email(type=None)

    @mock.patch("auction.models.Product.save")
    def test_delete(self, mock_save):
        """ should change status to deleted """
        self.product.delete()
        self.assertEqual(self.product.status, ProductStatus.DELETED)
        mock_save.assert_called_once_with()

    def test_delete_raise(self):
        """ should raise exception already deleted """
        self.product.status = ProductStatus.DELETED
        with self.assertRaisesMessage(
            GenericException, CodeError.ALREADY_DELETED.message
        ):
            self.product.delete()

    def test_delete_raise_solded(self):
        """ should raise exception already solded """
        self.product.status = ProductStatus.SOLD
        with self.assertRaisesMessage(
            GenericException, CodeError.ALREADY_SOLDED.message
        ):
            self.product.delete()

    @mock.patch("auction.models.product.product_try_to_make_a_deal.apply_async")
    def test_activate(self, mock_apply_deal):
        """ should activate """
        self.product.activate()
        self.assertEqual(self.product.status, ProductStatus.ACTIVE)
        mock_apply_deal.assert_called_once_with(
            args=[self.product.id], eta=self.product.end_date
        )

    def test_activate_raise(self):
        """ should raise exception """
        self.product.status = ProductStatus.ACTIVE
        self.product.save()
        with self.assertRaisesMessage(
            GenericException, CodeError.ALREADY_ACTIVATED.message
        ):
            self.product.activate()

    @mock.patch("auction.models.product.product_send_email.delay")
    def test_async_send_email(self, mock_delay):
        """ should call delay """
        type = "test"
        self.product.async_send_email(type)
        mock_delay.assert_called_once_with(
            product_id=self.product.id, type=type
        )

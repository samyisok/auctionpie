from typing import List
from unittest.mock import Mock, patch

from django.test import TestCase

from auction.models import Client, Deal, Product
from auction.tests.fixures import (amount_100, email, email_seller, password,
                                   password_seller, product_params)
from billing.models import Bill


class ModelDealTestCase(TestCase):
    """Deal model"""

    def setUp(self):
        self.buyer = Client.objects.create_user(email, password)
        self.seller = Client.objects.create_user(email_seller, password_seller)
        self.product_params = {"seller": self.seller, **product_params}
        self.product = Product.objects.create(**self.product_params)
        self.deal = Deal.objects.create(
            product=self.product, buyer=self.buyer, amount=amount_100
        )

    def test_get_commission(self):
        """ should return a commission """
        commission = self.deal.get_commission()
        self.assertEqual(commission, amount_100 * 30 / 100)

    def test_get_proceeds(self):
        """ should return a proceeds """
        proceeds = self.deal.get_proceeds()
        self.assertEqual(proceeds, amount_100 * 70 / 100)

    def test_create_bills(self):
        """ should create bills """

        bills: List[Bill] = self.deal.create_bills()
        bill1, bill2, bill3 = bills
        self.assertRegex(
            str(bill1),
            r"#\d+ sell: {amount}\({email}\)\(not_activated\)".format(
                amount=amount_100, email=email
            ),
        )
        self.assertRegex(
            str(bill2),
            r"#\d+ proceeds: {amount}\({email}\)\(not_activated\)".format(
                amount=amount_100, email=email_seller
            ),
        )
        self.assertRegex(
            str(bill3),
            r"#\d+ commission: {amount}\({email}\)\(not_activated\)".format(
                amount=amount_100 * 30 / 100, email=email_seller
            ),
        )

        # проверяем связки
        bill_sell, bill_proceeds, bill_commission = self.deal.bills.all()

        self.assertRegex(
            str(bill_sell),
            r"#\d+ sell: {amount}\({email}\)\(not_activated\)".format(
                amount=amount_100, email=email
            ),
        )
        self.assertRegex(
            str(bill_proceeds),
            r"#\d+ proceeds: {amount}\({email}\)\(not_activated\)".format(
                amount=amount_100, email=email_seller
            ),
        )
        self.assertRegex(
            str(bill_commission),
            r"#\d+ commission: {amount}\({email}\)\(not_activated\)".format(
                amount=amount_100 * 30 / 100, email=email_seller
            ),
        )

    @patch("auction.models.Deal.create_bills")
    def test_finalize(self, mock_create_bills):
        """ should call create_bills """
        mock_bill1, mock_bill2 = [Mock(), Mock()]
        mock_bill1.async_activate = Mock()
        mock_bill2.async_activate = Mock()
        mock_create_bills.return_value = [mock_bill1, mock_bill2]
        value = self.deal.finalize()
        self.assertEqual(value, None)
        mock_create_bills.assert_called_once_with()
        mock_bill1.async_activate.assert_called_once_with()
        mock_bill2.async_activate.assert_called_once_with()

    @patch("auction.models.deal.deal_finalize.delay", return_value=None)
    def test_async_finalize(self, mock_deal_finalize_delay):
        """ should call create_bills """
        value = self.deal.async_finalize()
        self.assertEqual(value, None)
        mock_deal_finalize_delay.assert_called_once_with(deal_id=self.deal.id)

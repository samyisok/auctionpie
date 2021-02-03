from datetime import timedelta
from decimal import Decimal
from typing import List
from unittest.mock import Mock, patch

from django.test import TestCase
from django.utils import timezone

from auction.models import Client, Deal, Product
from billing.models import Bill

email_buyer = "buyer@test.ru"
email_seller = "seller@test.ru"
amount = Decimal("100.00")
product_params = {
    "name": "product name",
    "description": "product desc",
    "start_price": Decimal(10),
    "buy_price": Decimal(20),
    "start_date": timezone.now(),
    "end_date": timezone.now() + timedelta(7),
}


class ModelDealTestCase(TestCase):
    """Deal model"""

    def setUp(self):
        self.buyer = Client.objects.create_user(email_buyer, "password")
        self.seller = Client.objects.create_user(email_seller, "password")
        self.product_params = {"seller": self.seller, **product_params}
        self.product = Product.objects.create(**self.product_params)
        self.deal = Deal.objects.create(
            product=self.product, buyer=self.buyer, amount=amount
        )

    def test_get_commission(self):
        """ should return a commission """
        commission = self.deal.get_commission()
        self.assertEqual(commission, amount * 30 / 100)

    def test_get_proceeds(self):
        """ should return a proceeds """
        proceeds = self.deal.get_proceeds()
        self.assertEqual(proceeds, amount * 70 / 100)

    def test_create_bills(self):
        """ should create bills """

        bills: List[Bill] = self.deal.create_bills()
        bill1, bill2, bill3 = bills
        self.assertEqual(
            str(bill1),
            "#1 sell: 100.00(buyer@test.ru)(not_activated)",
        )
        self.assertEqual(
            str(bill2),
            "#2 proceeds: 100.00(seller@test.ru)(not_activated)",
        )
        self.assertEqual(
            str(bill3),
            "#3 commission: 30.00(seller@test.ru)(not_activated)",
        )

        # проверяем связки
        bill_sell, bill_proceeds, bill_commission = self.deal.bills.all()

        self.assertEqual(
            str(bill_sell),
            "#1 sell: 100.00(buyer@test.ru)(not_activated)",
        )
        self.assertEqual(
            str(bill_proceeds),
            "#2 proceeds: 100.00(seller@test.ru)(not_activated)",
        )
        self.assertEqual(
            str(bill_commission),
            "#3 commission: 30.00(seller@test.ru)(not_activated)",
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

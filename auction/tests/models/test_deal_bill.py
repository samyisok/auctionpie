from django.test import TestCase

from auction.models import Client, Deal, DealBill, Product
from auction.tests.fixtures import (
    amount_100,
    email,
    email_seller,
    password,
    password_seller,
    product_params,
)
from billing.meta import BillType
from billing.models import Bill


class ModelDealBillTestCase(TestCase):
    """DealBill model"""

    def setUp(self):
        self.buyer = Client.objects.create_user(email, password)
        self.seller = Client.objects.create_user(email_seller, password_seller)
        self.product_params = {"seller": self.seller, **product_params}
        self.product = Product.objects.create(**self.product_params)
        self.deal = Deal.objects.create(
            product=self.product, buyer=self.buyer, amount=amount_100
        )
        self.bill = Bill.objects.create(
            client=self.deal.product.seller,
            bill_type=BillType.PROCEEDS,
            amount=self.deal.amount,
            vat=self.deal.buyer.vat,
        )
        self.deal.bills.add(self.bill)
        self.dealbill = DealBill.objects.get(deal=self.deal)

    def test_str(self):
        """ should return str """
        self.assertEqual(str(self.dealbill), f"{self.deal} - {self.bill}")

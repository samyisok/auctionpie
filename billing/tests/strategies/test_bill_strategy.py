from django.test import TestCase
from billing.models import (
    Bill,
)
from billing.meta import BillType, BillStatus
from billing.strategies import BillStrategyPrepay
from auction.models import Client
from decimal import Decimal


email = "emailfortest@test.ru"
amount = Decimal("100.00")
small_amount = Decimal("10.00")
vat = 20


class PrecreateMixin:
    def precreate_data(self):
        self.client = Client.objects.create_user(email, "password")
        self.bill_prepay = Bill.objects.create(
            client=self.client,
            bill_type=BillType.PREPAY,
            status=BillStatus.NOT_ACTIVATED,
            amount=amount,
            vat=vat,
        )
        self.bill_sell = Bill.objects.create(
            client=self.client,
            bill_type=BillType.SELL,
            status=BillStatus.NOT_ACTIVATED,
            amount=small_amount,
            vat=vat,
        )
        self.bill_commission = Bill.objects.create(
            client=self.client,
            bill_type=BillType.COMMISSION,
            status=BillStatus.NOT_ACTIVATED,
            amount=small_amount,
            vat=vat,
        )
        self.bill_proceeds = Bill.objects.create(
            client=self.client,
            bill_type=BillType.PROCEEDS,
            status=BillStatus.NOT_ACTIVATED,
            amount=small_amount,
            vat=vat,
        )


class BillStrategyPrepayTestCase(TestCase, PrecreateMixin):
    """prepay"""

    def setUp(self):
        self.precreate_data()
        self.strategy = BillStrategyPrepay(bill=self.bill_prepay)

    def test_matches(self):
        """ strategy should match bill prepay"""
        self.assertEqual(self.strategy.matches(self.bill_prepay), True)
        self.assertEqual(self.strategy.matches(self.bill_sell), False)

    def test_bill_activate(self):
        """ bill should be activated """
        bill = self.strategy.bill_activate()
        self.assertEqual(bill.status, BillStatus.ACTIVATED)

    def test_transaction_create(self):
        """ should create transaction """
        tnx = self.strategy.transaction_create()
        self.assertEqual(tnx.amount, self.bill_prepay.amount)

    def test_activate(self):
        """ should activate """
        bill = self.strategy.activate()

        self.assertEqual(
            self.strategy.transaction.amount, self.bill_prepay.amount
        )
        self.assertEqual(bill.status, BillStatus.ACTIVATED)
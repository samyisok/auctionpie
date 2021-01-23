from django.test import TestCase
from billing.models import (
    Bill,
)
from billing.meta import BillType, BillStatus
from billing.strategies import (
    BillStrategyPrepay,
    BillStrategySell,
    BillStrategyCommission,
    BillStrategyProceeds,
)
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


class BillStrategySellTestCase(TestCase, PrecreateMixin):
    """sell"""

    def setUp(self):
        self.precreate_data()
        self.strategy = BillStrategySell(bill=self.bill_sell)

    def test_matches(self):
        """ strategy should match bill prepay"""
        self.assertEqual(self.strategy.matches(self.bill_sell), True)
        self.assertEqual(self.strategy.matches(self.bill_prepay), False)

    def test_bill_activate(self):
        """ bill should be activated """
        bill = self.strategy.bill_activate()
        self.assertEqual(bill.status, BillStatus.ACTIVATED)

    def test_transaction_create(self):
        """ should create transaction """
        tnx = self.strategy.transaction_create()
        self.assertEqual(tnx.amount, -1 * self.bill_sell.amount)

    def test_activate(self):
        """ should activate """
        bill = self.strategy.activate()

        self.assertEqual(
            self.strategy.transaction.amount, -1 * self.bill_sell.amount
        )
        self.assertEqual(bill.status, BillStatus.ACTIVATED)


class BillStrategyCommissionTestCase(TestCase, PrecreateMixin):
    """ Commission """

    def setUp(self):
        self.precreate_data()
        self.strategy = BillStrategyCommission(bill=self.bill_commission)

    def test_matches(self):
        """ strategy should match bill prepay"""
        self.assertEqual(self.strategy.matches(self.bill_commission), True)
        self.assertEqual(self.strategy.matches(self.bill_prepay), False)

    def test_bill_activate(self):
        """ bill should be activated """
        bill = self.strategy.bill_activate()
        self.assertEqual(bill.status, BillStatus.ACTIVATED)

    def test_transaction_create(self):
        """ should create transaction """
        tnx = self.strategy.transaction_create()
        self.assertEqual(tnx.amount, -1 * self.bill_commission.amount)

    def test_activate(self):
        """ should activate """
        bill = self.strategy.activate()

        self.assertEqual(
            self.strategy.transaction.amount, -1 * self.bill_commission.amount
        )
        self.assertEqual(bill.status, BillStatus.ACTIVATED)


class BillStrategyProceedsTestCase(TestCase, PrecreateMixin):
    """proceeds"""

    def setUp(self):
        self.precreate_data()
        self.strategy = BillStrategyProceeds(bill=self.bill_proceeds)

    def test_matches(self):
        """ strategy should match bill prepay"""
        self.assertEqual(self.strategy.matches(self.bill_proceeds), True)
        self.assertEqual(self.strategy.matches(self.bill_prepay), False)

    def test_bill_activate(self):
        """ bill should be activated """
        bill = self.strategy.bill_activate()
        self.assertEqual(bill.status, BillStatus.ACTIVATED)

    def test_transaction_create(self):
        """ should create transaction """
        tnx = self.strategy.transaction_create()
        self.assertEqual(tnx.amount, self.bill_proceeds.amount)

    def test_activate(self):
        """ should activate """
        bill = self.strategy.activate()

        self.assertEqual(
            self.strategy.transaction.amount, self.bill_proceeds.amount
        )
        self.assertEqual(bill.status, BillStatus.ACTIVATED)

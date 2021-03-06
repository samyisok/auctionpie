from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase

from auction.models import Client
from billing.meta import BillStatus, BillType
from billing.models import Bill
from billing.strategies import (
    BillStrategyCommission,
    BillStrategyFactory,
    BillStrategyPrepay,
    BillStrategyProceeds,
    BillStrategySell,
)
from core.errors import CodeError, GenericException

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

    @patch("billing.models.Bill.create_transaction_deposit", return_value=None)
    def test_transaction_create_raise(self, mock):
        """ should raise exception if transaction not created """
        with self.assertRaisesMessage(
            GenericException, CodeError.TRANSACTION_NOT_CREATED.message
        ):
            self.strategy.transaction_create()

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

    @patch("billing.models.Bill.create_transaction_expense", return_value=None)
    def test_transaction_create_raise(self, mock):
        """ should raise exception if transaction not created """
        with self.assertRaisesMessage(
            GenericException, CodeError.TRANSACTION_NOT_CREATED.message
        ):
            self.strategy.transaction_create()

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

    @patch("billing.models.Bill.create_transaction_expense", return_value=None)
    def test_transaction_create_raise(self, mock):
        """ should raise exception if transaction not created """
        with self.assertRaisesMessage(
            GenericException, CodeError.TRANSACTION_NOT_CREATED.message
        ):
            self.strategy.transaction_create()

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

    @patch("billing.models.Bill.create_transaction_deposit", return_value=None)
    def test_transaction_create_raise(self, mock):
        """ should raise exception if transaction not created """
        with self.assertRaisesMessage(
            GenericException, CodeError.TRANSACTION_NOT_CREATED.message
        ):
            self.strategy.transaction_create()

    def test_activate(self):
        """ should activate """
        bill = self.strategy.activate()

        self.assertEqual(
            self.strategy.transaction.amount, self.bill_proceeds.amount
        )
        self.assertEqual(bill.status, BillStatus.ACTIVATED)


class BillStrategyFactoryTestCase(TestCase, PrecreateMixin):
    """ Strategy factory """

    def setUp(self):
        self.precreate_data()

    def test_get_strategy_prepay(self):
        """ should get correct strategy instance """
        strategy = BillStrategyFactory.get_strategy(self.bill_prepay)
        self.assertIsInstance(strategy, BillStrategyPrepay)

    def test_get_strategy_sell(self):
        """ should get correct strategy instance """
        strategy = BillStrategyFactory.get_strategy(self.bill_sell)
        self.assertIsInstance(strategy, BillStrategySell)

    def test_get_strategy_commission(self):
        """ should get correct strategy instance """
        strategy = BillStrategyFactory.get_strategy(self.bill_commission)
        self.assertIsInstance(strategy, BillStrategyCommission)

    def test_get_strategy_proceeds(self):
        """ should get correct strategy instance """
        strategy = BillStrategyFactory.get_strategy(self.bill_proceeds)
        self.assertIsInstance(strategy, BillStrategyProceeds)

    @patch("billing.strategies.BillStrategyFactory.strategies", return_value=[])
    def test_get_strategy_raise(self, mock_strategies):
        """ should raise value error """
        with self.assertRaisesMessage(
            ValueError, "Suitable strategy not found"
        ):
            BillStrategyFactory.get_strategy(self.bill_proceeds)

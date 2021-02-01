from decimal import Decimal

from django.test import TestCase

from auction.models import Client
from billing.meta import BillStatus, BillType
from billing.models import Bill, Transaction

email = "emailfortest@test.ru"
amount = Decimal("12.34")
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
            amount=amount / 2,
            vat=vat,
        )


class TransactionDepositTestCase(TestCase, PrecreateMixin):
    """Deposit"""

    def setUp(self):
        self.precreate_data()

    def test_str(self):
        """ str should be success """

        self.assertRegex(
            str(self.bill_prepay),
            r"^#\d+ prepay: 12.34\(emailfortest@test\.ru\)\(not_activated\)",
        )

    def test_activate(self):
        """ should activate a bill """
        bill = self.bill_prepay.activate()
        self.assertIsInstance(bill, Bill)
        self.assertEqual(bill.status, BillStatus.ACTIVATED)

    def test_create_transaction_deposit(self):
        """ should create a depostit transaction """
        transaction = self.bill_prepay.create_transaction_deposit()
        self.assertIsInstance(transaction, Transaction)
        self.assertEqual(transaction.amount, self.bill_prepay.amount)

    def test_create_transaction_expense(self):
        """ should create a expense transaction """
        transaction = self.bill_sell.create_transaction_expense()
        self.assertIsInstance(transaction, Transaction)
        self.assertEqual(transaction.amount, -1 * self.bill_sell.amount)

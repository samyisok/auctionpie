from decimal import Decimal

from django.test import TestCase

from auction.models import Client
from billing.meta import BillStatus, BillType, TransactionException
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
        """str should be success"""
        tnx = Transaction.deposit(
            amount=amount,
            client=self.client,
            bill=self.bill_prepay,
            comment="test",
        )

        self.assertEqual(str(tnx), f"#1 deposit: 12.34({email})")

    def test_deposit_success(self):
        """deposit should be success"""
        tnx = Transaction.deposit(
            amount=amount,
            client=self.client,
            bill=self.bill_prepay,
            comment="test",
        )

        tnx2 = Transaction.objects.get(id=tnx.id)

        self.assertIsInstance(tnx, Transaction)
        self.assertEqual(tnx.amount, amount)
        self.assertEqual(tnx.tnx_type, "deposit")
        self.assertEqual(tnx.comment, "test")
        self.assertIsNotNone(tnx2)

    def test_deposit_exception(self):
        """raise TransactionExceptuon with msg"""
        with self.assertRaisesMessage(
            TransactionException, "amount param should be positive"
        ):
            Transaction.deposit(
                amount=Decimal("-12.34"),
                client=self.client,
                bill=self.bill_prepay,
                comment="test",
            )


class TransactionExpenseTestCase(TestCase, PrecreateMixin):
    """Expense"""

    def setUp(self):
        self.precreate_data()

    def test_expense_success(self):
        """expense should be success"""
        tnx = Transaction.expense(
            amount=amount,
            client=self.client,
            bill=self.bill_sell,
            comment="test",
        )

        tnx2 = Transaction.objects.get(id=tnx.id)

        self.assertIsInstance(tnx, Transaction)
        self.assertEqual(tnx.amount, -1 * amount)
        self.assertEqual(tnx.tnx_type, "expense")
        self.assertEqual(tnx.comment, "test")
        self.assertIsNotNone(tnx2)

    def test_expense_exception(self):
        """raise TransactionExceptuon with msg"""
        with self.assertRaisesMessage(
            TransactionException, "amount param should be positive"
        ):
            Transaction.expense(
                amount=Decimal("-12.34"),
                client=self.client,
                bill=self.bill_sell,
                comment="test",
            )


class TransactionWithdrawTestCase(TestCase, PrecreateMixin):
    """Withdraw"""

    def setUp(self):
        self.precreate_data()
        self.deposit = Transaction.deposit(
            amount=amount, client=self.client, bill=self.bill_prepay
        )

    def test_withdraw_success(self):
        """withdraw should be success"""
        tnx = Transaction.withdraw(
            amount=amount,
            client=self.client,
            bill=self.bill_prepay,
            comment="test",
        )

        tnx2 = Transaction.objects.get(id=tnx.id)

        self.assertIsInstance(tnx, Transaction)
        self.assertEqual(tnx.amount, -1 * amount)
        self.assertEqual(tnx.tnx_type, "withdraw")
        self.assertEqual(tnx.comment, "test")
        self.assertIsNotNone(tnx2)

    def test_withdraw_exception_if_amount_negative(self):
        """raise TransactionExceptuon with msg"""
        with self.assertRaisesMessage(
            TransactionException, "amount param should be positive"
        ):
            Transaction.withdraw(
                amount=Decimal("-12.34"),
                client=self.client,
                bill=self.bill_prepay,
                comment="test",
            )

    def test_withdraw_exception_if_balance_not_enough(self):
        """raise TransactionExceptuon with msg"""
        with self.assertRaisesMessage(
            TransactionException, "not enough amount on balance"
        ):
            Transaction.withdraw(
                amount=Decimal("15.00"),
                client=self.client,
                bill=self.bill_prepay,
                comment="test",
            )


class TransactionCancellationTestCase(TestCase, PrecreateMixin):
    """Cancellation"""

    def setUp(self):
        self.precreate_data()

    def test_cancelation_success(self):
        """cancellation should be success"""
        tnx = Transaction.cancellation(
            amount=amount,
            client=self.client,
            bill=self.bill_sell,
            comment="test",
        )

        tnx2 = Transaction.objects.get(id=tnx.id)

        self.assertIsInstance(tnx, Transaction)
        self.assertEqual(tnx.amount, amount)
        self.assertEqual(tnx.tnx_type, "cancellation")
        self.assertEqual(tnx.comment, "test")
        self.assertIsNotNone(tnx2)

    def test_cancellation_exception(self):
        """raise TransactionExceptuon with msg"""
        with self.assertRaisesMessage(
            TransactionException, "amount param should be positive"
        ):
            Transaction.cancellation(
                amount=Decimal("-12.34"),
                client=self.client,
                bill=self.bill_sell,
                comment="test",
            )


class TransactionBalanceTestCase(TestCase, PrecreateMixin):
    """Balance"""

    def setUp(self):
        self.precreate_data()

        self.deposit = Transaction.deposit(
            amount=amount, client=self.client, bill=self.bill_prepay
        )
        self.expense = Transaction.expense(
            amount=amount / 2, client=self.client, bill=self.bill_sell
        )

    def test_balance_success(self):
        """should get correct balance """
        balance = Transaction.balance(client=self.client)

        self.assertEqual(balance, amount / 2)

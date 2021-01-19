from django.test import TestCase
from billing.models import Transaction, TransactionException
from auction.models import Client
from decimal import Decimal


email = "emailfortest@test.ru"
amount = Decimal("12.34")


class TransactionDepositTestCase(TestCase):
    """Deposit"""

    def setUp(self):
        self.client = Client.objects.create_user(email, "password")

    def test_str(self):
        """str should be success"""
        tnx = Transaction.deposit(
            amount=amount, client=self.client, comment="test"
        )

        self.assertEqual(str(tnx), f"#1 deposit: 12.34({email})")

    def test_deposit_success(self):
        """deposit should be success"""
        tnx = Transaction.deposit(
            amount=amount, client=self.client, comment="test"
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
                amount=Decimal("-12.34"), client=self.client, comment="test"
            )


class TransactionExpenseTestCase(TestCase):
    """Expense"""

    def setUp(self):
        self.client = Client.objects.create_user(email, "password")

    def test_expense_success(self):
        """expense should be success"""
        tnx = Transaction.expense(
            amount=amount, client=self.client, comment="test"
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
                amount=Decimal("-12.34"), client=self.client, comment="test"
            )


class TransactionWithdrawTestCase(TestCase):
    """Withdraw"""

    def setUp(self):
        self.client = Client.objects.create_user(email, "password")
        self.deposit = Transaction.deposit(amount=amount, client=self.client)

    def test_withdraw_success(self):
        """withdraw should be success"""
        tnx = Transaction.withdraw(
            amount=amount, client=self.client, comment="test"
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
                amount=Decimal("-12.34"), client=self.client, comment="test"
            )

    def test_withdraw_exception_if_balance_not_enough(self):
        """raise TransactionExceptuon with msg"""
        with self.assertRaisesMessage(
            TransactionException, "not enough amount on balance"
        ):
            Transaction.withdraw(
                amount=Decimal("15.00"), client=self.client, comment="test"
            )


class TransactionCancellationTestCase(TestCase):
    """Cancellationt"""

    def setUp(self):
        self.client = Client.objects.create_user(email, "password")

    def test__success(self):
        """cancellation should be success"""
        tnx = Transaction.cancellation(
            amount=amount, client=self.client, comment="test"
        )

        tnx2 = Transaction.objects.get(id=tnx.id)

        self.assertIsInstance(tnx, Transaction)
        self.assertEqual(tnx.amount, amount)
        self.assertEqual(tnx.tnx_type, "cancellation")
        self.assertEqual(tnx.comment, "test")
        self.assertIsNotNone(tnx2)

    def test_deposit_exception(self):
        """raise TransactionExceptuon with msg"""
        with self.assertRaisesMessage(
            TransactionException, "amount param should be positive"
        ):
            Transaction.cancellation(
                amount=Decimal("-12.34"), client=self.client, comment="test"
            )

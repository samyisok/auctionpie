from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.test import TestCase

from auction.models import Client
from billing.helpers.graphql import create_payment, get_balance
from billing.meta import BillStatus, BillType
from billing.models import Bill, Payment, Transaction
from billing.structures.graphql import ClientInput, CreatePaymentInput

email = "emailfortest@test.ru"
password = "password"
amount = Decimal("12.34")
vat = 20


class PrecreateMixin:
    def precreate_data(self):
        self.client = Client.objects.create_user(email, password)
        self.bill_prepay = Bill.objects.create(
            client=self.client,
            bill_type=BillType.PREPAY,
            status=BillStatus.NOT_ACTIVATED,
            amount=amount,
            vat=vat,
        )
        self.transaction = Transaction.deposit(
            amount=amount,
            client=self.client,
            bill=self.bill_prepay,
            comment="test",
        )


class HelperBalanceTestCase(TestCase, PrecreateMixin):
    """ helper balance func """

    def test_get_balance(self):
        """ should get zeroed balance even if there no transactions """
        self.client = Client.objects.create_user(email, password)
        client_input = ClientInput(client=self.client)
        self.assertEqual(get_balance(client_input), Decimal(0))

    def test_get_balance_with_amount(self):
        """ should get balance with amount """
        self.precreate_data()
        client_input = ClientInput(client=self.client)
        self.assertEqual(get_balance(client_input), Decimal(amount))


class HelperCreatePayment(TestCase):
    """ helper create payment """

    def setUp(self) -> None:
        self.client = Client.objects.create_user(email, password)

    @patch("billing.models.Payment.async_process")
    def test_create_payment(self, mock_async_process: MagicMock):
        """ should create payment """

        payment_system = "yoomoney"

        input = CreatePaymentInput(
            client=self.client, amount=amount, payment_system=payment_system
        )

        payment_id = create_payment(input=input)
        payment = Payment.objects.get(id=payment_id)

        mock_async_process.assert_called_once_with()

        self.assertEqual(payment.expected_amount, amount)
        self.assertEqual(payment.payment_system, payment_system)
        self.assertEqual(payment.description, "Предоплата")
        self.assertEqual(payment.client, self.client)

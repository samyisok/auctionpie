from decimal import Decimal

from django.test import TestCase

from auction.models import Client
from billing.helpers.graphql import get_balance
from billing.meta import BillStatus, BillType
from billing.models import Bill, Transaction
from billing.structures.graphql import ClientInput

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

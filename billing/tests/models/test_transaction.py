from django.test import TestCase
from billing.models import Transaction
from auction.models import Client
from decimal import Decimal


class TestBillingModels(TestCase):
    def test_model_str(self):
        client = Client.objects.create_user("test2222@test.ru", "123")

        client.save()

        tnx = Transaction.deposit(
            amount=Decimal("10.10"), client=client, comment="test"
        )

        self.assertEqual(str(tnx), "#1 deposit: 10.10(test2222@test.ru)")

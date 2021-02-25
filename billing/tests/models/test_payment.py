from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.test import TestCase

from auction.models import Client
from billing.models import Payment

email = "emailfortest@test.ru"
amount = Decimal("12.34")


class PaymentModelTestCase(TestCase):
    """Payment"""

    def setUp(self):
        self.client: Client = Client.objects.create_user(email, "password")
        self.payment: Payment = Payment.objects.create(
            client=self.client,
            expected_amount=amount,
            payment_system="dummy",
            description="",
        )

    @patch("billing.models.payment.payment_process.delay")
    def test_async_process(self, mock_delay: MagicMock):
        """ should call delay """
        self.payment.async_process()
        mock_delay.assert_called_once_with()

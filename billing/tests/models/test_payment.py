from decimal import Decimal
from unittest.mock import MagicMock, Mock, PropertyMock, call, patch

from django.test import TestCase
from django.utils import timezone

from auction.models import Client
from billing.meta import PaymentStatus
from billing.models import Payment
from core.errors import CodeError, GenericException

email = "emailfortest@test.ru"
amount = Decimal("12.34")
time = timezone.now()


class PaymentModelTestCase(TestCase):
    """Payment"""

    def setUp(self):
        psi = MagicMock(
            process_payment=MagicMock(), process_request=MagicMock()
        )

        self.mock_psi: MagicMock = patch.object(
            Payment,
            "payment_system_instance",
            new_callable=PropertyMock(return_value=psi),
        ).start()

        self.client: Client = Client.objects.create_user(email, "password")
        self.payment: Payment = Payment.objects.create(
            client=self.client,
            expected_amount=amount,
            payment_system="dummy",
            description="",
        )

        self.mock_save: Mock = patch.object(
            self.payment, "save", wraps=self.payment.save
        ).start()

        self.mock_timezone_now: Mock = patch(
            "billing.models.payment.timezone.now", wraps=timezone.now
        ).start()
        self.mock_timezone_now.return_value = time

    @patch("billing.models.payment.payment_process.delay")
    def test_async_process(self, mock_delay: MagicMock):
        """ should call delay """
        self.payment.async_process()
        mock_delay.assert_called_once_with()

    def test_process(self):
        """ should call process_payment """
        self.payment.process()
        self.mock_psi.process_payment.assert_called_once_with()

    def test_process_request(self):
        """ should call process_request """
        self.payment.process_request()
        self.mock_psi.process_request.assert_called_once_with()

    @patch.object(Payment, "create_bill")
    def test_set_payed(self, mock_create_bill: MagicMock):
        """ should update status and create bill """
        self.payment.set_payed(amount=amount)

        mock_create_bill.assert_called_once_with()
        self.mock_save.assert_called_with()
        self.mock_timezone_now.assert_has_calls([call(), call()])

        result_payment: Payment = Payment.objects.get(id=self.payment.id)
        self.assertEqual(amount, result_payment.amount)
        self.assertEqual(time, result_payment.payed_date)
        self.assertEqual(PaymentStatus.PAYED, result_payment.status)

    def test_set_payed_exception(self):
        """ should raise wrong status exception """
        statuses = [
            status.value
            for status in PaymentStatus
            if status.value not in self.payment.statuses_allowed_to_be_payed
        ]

        for status in statuses:
            with self.assertRaisesMessage(
                GenericException, CodeError.WRONG_STATUS.message
            ):
                self.payment.status = status
                self.payment.save()
                self.payment.set_payed(amount=amount)

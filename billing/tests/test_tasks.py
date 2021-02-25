from unittest.mock import Mock, patch

from django.test import TestCase

from billing.tasks import bill_activate, payment_process


class TaskBillActivateTestCase(TestCase):
    """ should activate a bill """

    @patch("django.apps.apps.get_model")
    def test_bill_activate(
        self,
        mock_get_model,
    ):
        """ should call activate """
        mock_bill = Mock(activate=Mock())

        mock_bill_model = Mock(objects=Mock(get=Mock(return_value=mock_bill)))

        mock_get_model.return_value = mock_bill_model
        bill_activate(42)

        mock_get_model.assert_called_once_with("billing", "Bill")
        mock_bill_model.objects.get.assert_called_once_with(id=42)
        mock_bill.activate.assert_called_once_with()


class TaskPaymentProcessTestCase(TestCase):
    """ should process payment """

    @patch("django.apps.apps.get_model")
    def test_payment_process(
        self,
        mock_get_model,
    ):
        """ should call process """
        mock_payment = Mock(process=Mock())

        mock_payment_model = Mock(
            objects=Mock(get=Mock(return_value=mock_payment))
        )

        mock_get_model.return_value = mock_payment_model
        payment_process(42)

        mock_get_model.assert_called_once_with("billing", "Payment")
        mock_payment_model.objects.get.assert_called_once_with(id=42)
        mock_payment.process.assert_called_once_with()

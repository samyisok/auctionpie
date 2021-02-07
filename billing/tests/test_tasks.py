from unittest.mock import Mock, patch

from django.test import TestCase

from billing.tasks import bill_activate


class TaskBillActivateTestCase(TestCase):
    """ should finalize deal """

    @patch("django.apps.apps.get_model")
    def test_product_send_email(
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

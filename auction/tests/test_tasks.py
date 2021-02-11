from unittest.mock import Mock, patch

from celery.exceptions import Retry
from django.test import TestCase

from auction.models import Client, Product
from auction.tasks import (
    deal_finalize,
    deal_send_email,
    product_send_email,
    product_try_to_make_a_deal,
)
from auction.tests.fixtures import email_seller, password, product_params


class TaskProductTryToMakeADealTestCase(TestCase):
    """ product_try_to_make_a_deal """

    def setUp(self):
        self.seller = Client.objects.create_user(email_seller, password)
        self.product_params = {"seller": self.seller, **product_params}
        self.product = Product.objects.create(**self.product_params)

    @patch("auction.models.Product.is_ready_to_make_a_deal", return_value=True)
    @patch("auction.models.Product.make_a_deal", return_value=True)
    def test_product_try_to_make_a_deal(self, mock_make_a_deal, mock_is_ready):
        """ should call make_a_deal """
        product_try_to_make_a_deal(self.product.id)
        mock_make_a_deal.assert_called_once_with()
        mock_is_ready.assert_called_once_with()

    @patch("auction.tasks.product_try_to_make_a_deal.retry")
    @patch("auction.models.Product.is_ready_to_make_a_deal", return_value=False)
    def test_product_try_to_make_a_deal_raise_retry(
        self, mock_is_ready, mock_retry
    ):
        """ should raise retry exception """
        mock_retry.side_effect = Retry()
        with self.assertRaises(Retry):
            product_try_to_make_a_deal(self.product.id)
            mock_is_ready.assert_called_once_with()


class TaskProductSendEmalTestCase(TestCase):
    """ should call send email from product """

    @patch("django.apps.apps.get_model")
    def test_product_send_email(
        self,
        mock_get_model,
    ):
        """ should call send email """
        mock_product = Mock(send_email=Mock())

        mock_product_model = Mock(
            objects=Mock(get=Mock(return_value=mock_product))
        )

        mock_get_model.return_value = mock_product_model
        product_send_email(42, "type")

        mock_get_model.assert_called_once_with("auction", "Product")
        mock_product_model.objects.get.assert_called_once_with(id=42)
        mock_product.send_email.assert_called_once_with("type")


class TaskDealFinalizeTestCase(TestCase):
    """ should finalize deal """

    @patch("django.apps.apps.get_model")
    def test_product_send_email(
        self,
        mock_get_model,
    ):
        """ should call finalize """
        mock_deal = Mock(finalize=Mock())

        mock_deal_model = Mock(objects=Mock(get=Mock(return_value=mock_deal)))

        mock_get_model.return_value = mock_deal_model
        deal_finalize(42)

        mock_get_model.assert_called_once_with("auction", "Deal")
        mock_deal_model.objects.get.assert_called_once_with(id=42)
        mock_deal.finalize.assert_called_once_with()


class TaskDealSendEmailTestCase(TestCase):
    """ should send email """

    def test_deal_send_email(self):
        """ should get nothing not implemented yet """
        deal = None
        type = None
        self.assertIsNone(deal_send_email(deal, type))

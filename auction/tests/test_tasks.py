from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from celery.exceptions import Retry
from django.test import TestCase
from django.utils import timezone

from auction.models import Client, Product
from auction.tasks import product_try_to_make_a_deal

email_seller = "seller@test.ru"
amount = Decimal("12.34")
product_params = {
    "name": "product name",
    "description": "product desc",
    "start_price": Decimal(10),
    "buy_price": Decimal(20),
    "start_date": timezone.now(),
    "end_date": timezone.now() + timedelta(7),
}


class TaskProductTryToMakeADealTestCase(TestCase):
    """ product_try_to_make_a_deal """

    def setUp(self):
        self.seller = Client.objects.create_user(email_seller, "password")
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

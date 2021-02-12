from unittest.mock import MagicMock, patch

from django.test import TestCase

from auction.models import Client
from auction.tests.fixtures import email, password


class ModelsClientManagerTestCase(TestCase):
    """client model manager test"""

    @patch("auction.models.client.Client.objects._db", return_value="test")
    @patch("auction.models.client.Client.objects.model")
    @patch(
        "auction.models.client.ClientManager.normalize_email",
        return_value=email,
    )
    def test_create_user(
        self,
        mock_normalize_email: MagicMock,
        mock_model: MagicMock,
        mock__db: MagicMock,
    ):
        """ should create user """
        mock_client = MagicMock(set_password=MagicMock(), save=MagicMock())
        mock_model.return_value = mock_client

        client: Client = Client.objects.create_user(email, password)

        mock_normalize_email.assert_called_once_with(email)
        mock_model.assert_called_once_with(email=email)
        mock_client.set_password.assert_called_once_with(password)
        mock_client.save.assert_called_once_with(using=mock__db)
        self.assertIs(mock_client, client)

    def test_create_user_raise(self):
        """ should raise ValueError """
        with self.assertRaisesMessage(
            ValueError, "Users must have an email address"
        ):
            Client.objects.create_user(None, password)

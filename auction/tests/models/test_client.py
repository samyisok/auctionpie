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

    @patch("auction.models.client.Client.objects._db", return_value="test")
    @patch(
        "auction.models.client.ClientManager.create_user",
    )
    def test_create_superuser(
        self,
        mock_create_user: MagicMock,
        mock__db: MagicMock,
    ):
        """ should create_super_user """
        mock_client = MagicMock(save=MagicMock(), is_admin=False)
        mock_create_user.return_value = mock_client
        client: Client = Client.objects.create_superuser(email, password)

        mock_create_user.assert_called_once_with(email, password=password)
        self.assertIs(client, mock_client)
        self.assertEqual(client.is_admin, True)
        mock_client.save.assert_called_once_with(using=mock__db)

    def test_normalize_email(self):
        """ should correct normalize email """
        email = "TEST@EMAIL.COM"
        result = Client.objects.normalize_email(email)
        self.assertEqual(result, "TEST@email.com")

    def test_normalize_email_raise(self):
        """ should return raise ValueError if uncorrect """
        email = "uncorrect"
        with self.assertRaisesMessage(ValueError, "Uncorrect email"):
            Client.objects.normalize_email(email)


class ModelsClientTestCase(TestCase):
    """ model client test """

    def setUp(self):
        self.client: Client = Client(email=email, password=password)

    @patch("django.contrib.auth.models.AbstractBaseUser.clean")
    @patch(
        "auction.models.client.ClientManager.normalize_email",
        return_value=email,
    )
    def test_clean(
        self, mock_normalize_email: MagicMock, mock_clean: MagicMock
    ):
        """ should call normalize_email and super """
        self.client.clean()
        mock_clean.assert_called_once_with()
        mock_normalize_email.assert_called_once_with(email)

    @patch("auction.models.client.send_mail")
    def test_email_user(self, mock_send_mail: MagicMock):
        """ should email user """
        args = ["subject", "message", "from@company.ru"]
        self.client.email_user(*args)
        mock_send_mail.assert_called_once_with(*args, [email])

    def test_str(self):
        """ should return email """
        self.assertEqual(str(self.client), email)

    def test_has_perm(self):
        """ should return is_admin True """
        self.client.is_admin = True
        self.client.save()
        self.assertTrue(self.client.has_perm("perm_name"))

    def test_has_module_perms(self):
        """ should return is_admin True """
        self.client.is_admin = True
        self.client.save()
        self.assertTrue(self.client.has_module_perms("billing"))

    def test_is_staff(self):
        """ should return is_admin True """
        self.client.is_admin = True
        self.client.save()
        self.assertTrue(self.client.is_staff)

    def test_is_superuser(self):
        """ should return is_admin True """
        self.client.is_admin = True
        self.client.save()
        self.assertTrue(self.client.is_superuser)

    def test_vat(self):
        """ should return company vat """
        self.assertEqual(self.client.vat, self.client.company.vat)

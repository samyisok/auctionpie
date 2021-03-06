from typing import Any, Optional

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from auction.models.company import Company


class ClientManager(BaseUserManager):  # type: ignore #django-stubs/pull/360
    def create_user(self, email: str, password: str) -> "Client":
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        client: "Client" = self.model(
            email=self.normalize_email(email),
        )

        client.set_password(password)
        client.save(using=self._db)
        return client

    def create_superuser(self, email: str, password: str) -> "Client":
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        client = self.create_user(
            email,
            password=password,
        )
        client.is_admin = True
        client.save(using=self._db)
        return client

    @classmethod
    def normalize_email(cls, email: Optional[str] = None) -> str:
        """
        Normalize the email address by lowercasing the domain part of it.
        """
        email = email or ""
        try:
            email_name, domain_part = email.strip().rsplit("@", 1)
        except ValueError:
            raise ValueError("Uncorrect email")
        else:
            email = email_name + "@" + domain_part.lower()
        return email


class AbstractClient(AbstractBaseUser):
    """
    An abstract base class implementing a fully featured User model

    email and password are required. Other fields are optional.
    """

    email = models.EmailField(_("email address"), blank=True)
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    is_admin = models.BooleanField(default=False)

    objects = ClientManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"

    class Meta:
        verbose_name = _("client")
        verbose_name_plural = _("clients")
        abstract = True

    def __str__(self) -> str:
        return self.email

    def clean(self) -> None:
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(
        self, subject: str, message: str, from_email: Optional[str] = None
    ) -> int:
        """Send an email to this user."""
        return send_mail(subject, message, from_email, [self.email])

    def has_perm(self, perm: Any, obj: Optional[Any] = None) -> bool:
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label: Any) -> bool:
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    @property
    def is_staff(self) -> bool:
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    @property
    def is_superuser(self) -> bool:
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class FaceTypes(models.TextChoices):
    IND = 1, "Физ лицо"
    LTD = 2, "Юр лицо"
    ENT = 3, "ИП"
    GOV = 4, "Бюджет"


class Client(AbstractClient):
    email = models.EmailField(max_length=128, unique=True)
    password = models.CharField(max_length=128)
    cdate = models.DateTimeField(auto_now=False, auto_now_add=True)
    mdate = models.DateTimeField(auto_now=True, auto_now_add=False)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, default=settings.DEFAULT_COMPANY
    )
    face_id = models.IntegerField(
        choices=FaceTypes.choices,
        default=FaceTypes.IND,
    )
    last_login = models.DateTimeField(blank=True, null=True)

    @property
    def vat(self) -> int:
        return self.company.vat

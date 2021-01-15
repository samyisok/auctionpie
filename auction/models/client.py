from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.utils import timezone


class ClientManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        client = self.model(
            email=self.normalize_email(email),
        )

        client.set_password(password)
        client.save(using=self._db)
        return client

    @classmethod
    def normalize_email(cls, email):
        """
        Normalize the email address by lowercasing the domain part of it.
        """
        email = email or ""
        try:
            email_name, domain_part = email.strip().rsplit("@", 1)
        except ValueError:
            pass
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

    objects = ClientManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = _("client")
        verbose_name_plural = _("clients")
        abstract = True

    def __str__(self):
        return self.email

    def clean(self):
        super().clean()
        self.email = self.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Client(AbstractClient):
    FACES = [
        (1, u"Физ лицо"),
        (2, u"Юр лицо"),
        (3, u"ИП"),
        (4, u"Бюджет"),
    ]

    email = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=128)
    cdate = models.DateTimeField(auto_now=False, auto_now_add=True)
    mdate = models.DateTimeField(auto_now=True, auto_now_add=False)
    company_id = models.IntegerField(default=1)
    is_confirmed = models.BooleanField(default=False)
    face_id = models.IntegerField(
        choices=FACES,
        default=1,
    )
    last_login = models.DateTimeField(blank=True, null=True)

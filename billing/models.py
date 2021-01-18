from django.db import models
from auction.models import Client
from django.utils import timezone


class TransactionType(models.TextChoices):
    DEPOSIT = "deposit", "Зачисление на аккаунт пользователя"
    EXPENSE = "expesne", "Списание за услуги с аккаунта пользователя"
    WITHDRAW = "withdraw", "Вывод средств с аккаунта пользователя во вне"
    CANCELLATION = (
        "cancellation ",
        "Пополнение счета, средствами с отмены списания",
    )


class Transaction(models.Model):
    """
    транзакции баланса
    """

    client = models.ForeignKey(
        Client,
        verbose_name="Владелец транзакции",
        on_delete=models.CASCADE,
    )
    tnx_type = models.CharField(
        "Тип транзакции",
        choices=TransactionType.choices,
        max_length=32,
    )
    amount = models.DecimalField(
        "Сумма операции",
        max_digits=19,
        decimal_places=2,
    )
    cdate = models.DateTimeField("Дата создания", default=timezone.now)
    mdate = models.DateTimeField(
        "Дата изменения",
        auto_now=True,
        auto_now_add=False,
    )
    comment = models.CharField("Комментарий", max_length=128)

    def __str__(self):
        return f"#{self.id} {self.tnx_type}: {self.amount}({self.client})"

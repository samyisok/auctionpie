from __future__ import annotations

from django.db import models
from auction.models import Client
from django.utils import timezone
from decimal import Decimal


class TransactionException(Exception):
    pass


class TransactionType(models.TextChoices):
    DEPOSIT = "deposit", "Зачисление на аккаунт пользователя"
    EXPENSE = "expense", "Списание за услуги с аккаунта пользователя"
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

    @classmethod
    def deposit(
        cls,
        client: Client,
        amount: Decimal,
        comment: str = None,
    ) -> Transaction:
        """
        Создание депозита
        """
        if amount <= 0:
            raise TransactionException("amount param should be positive")

        txn = cls(
            client=client,
            amount=amount,
            tnx_type=TransactionType.DEPOSIT,
            comment=comment,
        )

        txn.save()

        return txn

    @classmethod
    def expense(
        cls,
        client: Client,
        amount: Decimal,
        comment: str = None,
    ) -> Transaction:
        """
        Создание списания
        """
        if amount <= 0:
            raise TransactionException("amount param should be positive")
        # TODO подумать будем ли уходить в минус или нет при списаниях.
        txn = cls(
            client=client,
            amount=-amount,
            tnx_type=TransactionType.EXPENSE,
            comment=comment,
        )

        txn.save()

        return txn

    @classmethod
    def withdraw(
        cls,
        client: Client,
        amount: Decimal,
        comment: str = None,
    ) -> Transaction:
        """
        Вывод средств
        """
        if amount <= 0:
            raise TransactionException("amount param should be positive")

        if cls.balance(client=client) < amount:
            raise TransactionException("not enough amount on balance")

        txn = cls(
            client=client,
            amount=-amount,
            tnx_type=TransactionType.WITHDRAW,
            comment=comment,
        )

        txn.save()

        return txn

    @classmethod
    def cancellation(
        cls,
        client: Client,
        amount: Decimal,
        comment: str = None,
    ) -> Transaction:
        """
        создание отмены
        """
        if amount <= 0:
            raise TransactionException("amount param should be positive")

        txn = cls(
            client=client,
            amount=amount,
            tnx_type=TransactionType.CANCELLATION,
            comment=comment,
        )

        txn.save()

        return txn

    @classmethod
    def balance(cls, client: Client) -> Decimal:
        """
        получение баланса клиента
        """
        where = models.Q(client__exact=client)

        result = cls.objects.filter(where).aggregate(
            amount=models.Sum("amount")
        )

        return result["amount"] or Decimal(0)

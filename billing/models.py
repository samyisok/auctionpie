from __future__ import annotations

from django.db import models
from auction.models import Client
from django.utils import timezone
from decimal import Decimal


class ModelAbstract(models.Model):
    cdate = models.DateTimeField("Дата создания", default=timezone.now)
    mdate = models.DateTimeField(
        "Дата изменения",
        auto_now=True,
        auto_now_add=False,
    )

    class Meta:
        abstract = True


class BillException(Exception):
    pass


class BillType(models.TextChoices):
    """
    prepay - предоплаты через платежные системы (+)
    sell - реализации услуги, например клиент купил товар, (-)
    то он создаст себе счет который sell, и затем транзакцию в балансе
    commission - счет на уплату доп расходов (-)
    proceeds - выручка с продажи товара (+)
    """

    PREPAY = "prepay", "предоплата на счет"
    SELL = "sell", "реализация товара или услуги"
    COMMISSION = "commission", "Плата за оказание услуги продажи"
    PROCEEDS = "proceeds", "Выручка"


class BillStatus(models.TextChoices):
    """
    status flow:
        not_activated->activated->cancelled

    Когда создаем счет, создаем его всегда не активированым.
    Когда активируем делаем некоторые обязательные действия(создаем движение на балансе)
    Когда отменяем, то выполняем логику рефанда(В нашем случае
    полный рефанд, но нужно подумать о том как делать частичный)
    и создаем позиции баланса с отменой.
    """

    NOT_ACTIVATED = "not_activated", "Счет не активирован"
    ACTIVATED = "activated", "Счет активирован"
    CANCELLED = "cancelled", "Счет отменен"


class Bill(ModelAbstract):
    """
    Счета

    Необходимо для того чтобы нести доп.информацию по балансу, зачем, почему, откуда.
    """

    client = models.ForeignKey(
        Client,
        verbose_name="Владелец счета",
        on_delete=models.CASCADE,
    )
    bill_type = models.CharField(
        "Тип счета", max_length=32, choices=BillType.choices
    )
    status = models.CharField(
        "статус счета",
        max_length=32,
        choices=BillStatus.choices,
        default=BillStatus.NOT_ACTIVATED,
    )
    amount = models.DecimalField("Сумма счета", max_digits=19, decimal_places=2)
    vat = models.IntegerField("НДС")

    def __str__(self):
        return f"#{self.id} {self.bill_type}: {self.amount}({self.client})({self.status})"

    def activate(self):
        """ Метод активации счета, в момент активации проводим транзакцию по балансу """
        method_name = f"create_tnx_{self.bill_type}"
        tnx = None
        if hasattr(self, method_name) and callable(
            method := getattr(self, method_name)
        ):
            tnx = method()
        else:
            raise BillException("unexpected activation method")

        if not isinstance(tnx, Transaction):
            raise BillException("transaction was not created")

        self.status = BillStatus.ACTIVATED
        self.save()

        return self

    def create_tnx_prepay(self):
        """создания пополнения на баланс"""
        return Transaction.deposit(
            client=self.client, bill=self, amount=self.amount
        )

    def create_tnx_sell(self):
        """создания списания на баланс"""
        return Transaction.expense(
            client=self.client, bill=self, amount=self.amount
        )

    def create_tnx_commission(self):
        """создания списания на баланс"""
        return Transaction.expense(
            client=self.client, bill=self, amount=self.amount
        )

    def create_tnx_proceeds(self):
        """создания пополнения на баланс"""
        return Transaction.deposit(
            client=self.client, bill=self, amount=self.amount
        )


class TransactionException(Exception):
    pass


class TransactionType(models.TextChoices):
    DEPOSIT = "deposit", "Зачисление на аккаунт пользователя"
    EXPENSE = "expense", "Списание за услуги с аккаунта пользователя"
    WITHDRAW = "withdraw", "Вывод средств с аккаунта пользователя во вне"
    CANCELLATION = (
        "cancellation",
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
    # У нас не должно быть транзакций без счета, но счет может иметь несколько транзакций
    bill = models.ForeignKey(
        Bill, verbose_name="Счет", on_delete=models.CASCADE
    )
    comment = models.CharField("Комментарий", max_length=128, null=True)
    cdate = models.DateTimeField("Дата создания", default=timezone.now)
    mdate = models.DateTimeField(
        "Дата изменения",
        auto_now=True,
        auto_now_add=False,
    )

    def __str__(self):
        return f"#{self.id} {self.tnx_type}: {self.amount}({self.client})"

    @classmethod
    def deposit(
        cls,
        client: Client,
        bill: Bill,
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
            bill=bill,
            tnx_type=TransactionType.DEPOSIT,
            comment=comment,
        )

        txn.save()

        return txn

    @classmethod
    def expense(
        cls,
        client: Client,
        bill: Bill,
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
            bill=bill,
            tnx_type=TransactionType.EXPENSE,
            comment=comment,
        )

        txn.save()

        return txn

    @classmethod
    def withdraw(
        cls,
        client: Client,
        bill: Bill,
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
            bill=bill,
            tnx_type=TransactionType.WITHDRAW,
            comment=comment,
        )

        txn.save()

        return txn

    @classmethod
    def cancellation(
        cls,
        client: Client,
        bill: Bill,
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
            bill=bill,
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

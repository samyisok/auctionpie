from django.db import models


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


class TransactionType(models.TextChoices):
    DEPOSIT = "deposit", "Зачисление на аккаунт пользователя"
    EXPENSE = "expense", "Списание за услуги с аккаунта пользователя"
    WITHDRAW = "withdraw", "Вывод средств с аккаунта пользователя во вне"
    CANCELLATION = (
        "cancellation",
        "Пополнение счета, средствами с отмены списания",
    )

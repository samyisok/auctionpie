from billing.models import (
    Bill,
    BillType,
    BillStatus,
    Transaction,
    BillException,
)
from typing import Tuple, Optional


class BillStrategy:
    """
    Базовый Класс стратегий счетов
    """

    bill_type: Tuple[str, str]
    bill: Bill
    transaction: Optional[Transaction]

    def __init__(self, bill: Bill) -> None:
        self.bill = bill

    @classmethod
    def matches(cls, bill: Bill) -> bool:
        return bill.bill_type is cls.bill_type

    def activate(self) -> Bill:
        raise NotImplementedError

    def bill_activate(self) -> Bill:
        self.bill.status = BillStatus.ACTIVATED
        self.bill.save()

        return self.bill

    def transaction_create_deposit(self) -> Transaction:
        self.transaction = Transaction.deposit(
            client=self.bill.client, bill=self.bill, amount=self.bill.amount
        )

        if not isinstance(self.transaction, Transaction):
            raise BillException("transaction was not created")

        return self.transaction

    def transaction_create_expense(self) -> Transaction:
        self.transaction = Transaction.expense(
            client=self.bill.client, bill=self.bill, amount=self.bill.amount
        )

        if not isinstance(self.transaction, Transaction):
            raise BillException("transaction was not created")

        return self.transaction


class BillStrategyPrepay(BillStrategy):
    """Стратегия предоплаты"""

    bill_type = BillType.PREPAY

    def activate(self) -> Bill:
        """ Метод активации счета, в момент активации проводим транзакцию по балансу """
        self.transaction_create_deposit()

        return self.bill_activate()


class BillStrategySell(BillStrategy):
    """Стратегия реализации"""

    bill_type = BillType.SELL

    def activate(self) -> Bill:
        """ Метод активации счета, в момент активации проводим транзакцию по балансу """
        self.transaction_create_expense()

        return self.bill_activate()


class BillStrategyCommission(BillStrategy):
    """Стратегия коммиссионых"""

    bill_type = BillType.COMMISSION

    def activate(self) -> Bill:
        """ Метод активации счета, в момент активации проводим транзакцию по балансу """
        self.transaction_create_expense()

        return self.bill_activate()


class BillStrategyProceeds(BillStrategy):
    """Стратегия выручки"""

    bill_type = BillType.PROCEEDS

    def activate(self) -> Bill:
        """ Метод активации счета, в момент активации проводим транзакцию по балансу """
        self.transaction_create_deposit()

        return self.bill_activate()


class BillStrategyFactory:
    """ Фабрика для получения стретегий счетов """

    strategies = [
        BillStrategyPrepay,
        BillStrategySell,
        BillStrategyCommission,
        BillStrategyProceeds,
    ]

    @classmethod
    def get_strategy(cls, bill):
        """Получаем нужную стратегию"""
        for strategy_class in cls.strategies:
            # стратегия подходит под счет
            if strategy_class.matches(bill):
                # Возвращаем инстанс стратегии
                return strategy_class(bill=bill)
        raise ValueError("Suitable strategy not found")

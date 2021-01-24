from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from billing.models import Bill, Transaction

from typing import Optional, Tuple

from billing.meta import BillException, BillStatus, BillType


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

    def transaction_create(self) -> Transaction:
        raise NotImplementedError


class BillStrategyDeposit(BillStrategy):
    def transaction_create(self) -> Transaction:
        self.transaction = self.bill.create_transaction_deposit()

        if self.transaction is None:
            raise BillException("transaction was not created")

        return self.transaction


class BillStrategyExpense(BillStrategy):
    def transaction_create(self) -> Transaction:
        self.transaction = self.bill.create_transaction_expense()

        if self.transaction is None:
            raise BillException("transaction was not created")

        return self.transaction


class BillStrategyPrepay(BillStrategyDeposit):
    """Стратегия предоплаты"""

    bill_type = BillType.PREPAY

    def activate(self) -> Bill:
        """ Метод активации счета, в момент активации проводим транзакцию по балансу """
        self.transaction_create()

        return self.bill_activate()


class BillStrategySell(BillStrategyExpense):
    """Стратегия реализации"""

    bill_type = BillType.SELL

    def activate(self) -> Bill:
        """ Метод активации счета, в момент активации проводим транзакцию по балансу """
        self.transaction_create()

        return self.bill_activate()


class BillStrategyCommission(BillStrategyExpense):
    """Стратегия коммиссионых"""

    bill_type = BillType.COMMISSION

    def activate(self) -> Bill:
        """ Метод активации счета, в момент активации проводим транзакцию по балансу """
        self.transaction_create()

        return self.bill_activate()


class BillStrategyProceeds(BillStrategyDeposit):
    """Стратегия выручки"""

    bill_type = BillType.PROCEEDS

    def activate(self) -> Bill:
        """ Метод активации счета, в момент активации проводим транзакцию по балансу """
        self.transaction_create()

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

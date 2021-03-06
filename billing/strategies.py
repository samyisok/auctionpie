from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from billing.models import Bill, Transaction

from typing import Optional

from billing.meta import BillStatus, BillType
from core.errors import CodeError


class BillStrategy:
    """
    Базовый Класс стратегий счетов
    """

    bill_type: str
    bill: Bill
    transaction: Optional[Transaction]

    def __init__(self, bill: Bill) -> None:
        self.bill = bill

        # Не позволяем создовать стратегии без типа счета
        if self.bill_type is None:
            raise NotImplementedError

    @classmethod
    def matches(cls, bill: Bill) -> bool:
        """ метод проверки выбора стратегии в фабрике стратегий """
        return bill.bill_type == cls.bill_type

    def bill_activate(self) -> Bill:
        """ Активация счета """
        self.bill.status = BillStatus.ACTIVATED
        self.bill.save()

        return self.bill

    def transaction_create(self) -> Transaction:
        raise NotImplementedError

    def activate(self) -> Bill:
        """ Метод активации счета, в момент активации проводим транзакцию по балансу """
        self.transaction_create()

        return self.bill_activate()


class BillStrategyDeposit(BillStrategy):
    def transaction_create(self) -> Transaction:
        self.transaction = self.bill.create_transaction_deposit()

        if self.transaction is None:
            raise CodeError.TRANSACTION_NOT_CREATED.exception

        return self.transaction


class BillStrategyExpense(BillStrategy):
    def transaction_create(self) -> Transaction:
        self.transaction = self.bill.create_transaction_expense()

        if self.transaction is None:
            raise CodeError.TRANSACTION_NOT_CREATED.exception

        return self.transaction


class BillStrategyPrepay(BillStrategyDeposit):
    """Стратегия предоплаты"""

    bill_type: str = BillType.PREPAY.value


class BillStrategySell(BillStrategyExpense):
    """Стратегия реализации"""

    bill_type: str = BillType.SELL.value


class BillStrategyCommission(BillStrategyExpense):
    """Стратегия коммиссионых"""

    bill_type: str = BillType.COMMISSION.value


class BillStrategyProceeds(BillStrategyDeposit):
    """Стратегия выручки"""

    bill_type: str = BillType.PROCEEDS.value


class BillStrategyFactory:
    """ Фабрика для получения стретегий счетов """

    strategies = [
        BillStrategyPrepay,
        BillStrategySell,
        BillStrategyCommission,
        BillStrategyProceeds,
    ]

    @classmethod
    def get_strategy(cls, bill: Bill) -> BillStrategy:
        """Получаем нужную стратегию"""
        for strategy_class in cls.strategies:
            # стратегия подходит под счет
            if strategy_class.matches(bill):
                # Возвращаем инстанс стратегии
                return strategy_class(bill=bill)
        raise ValueError("Suitable strategy not found")

from typing import List

from django.conf import settings
from django.db import models

from auction.models import Client
from auction.models.base import ModelAbstract
from auction.tasks import deal_finalize
from billing.meta import BillType
from billing.models import Bill


class Deal(ModelAbstract):
    """
    Фиксируем аукцион в сделках.

    на основе сделок формируем счета и движения по балансу
    и делаем связь между сделками и счетами.

    """

    product = models.OneToOneField(
        "auction.Product", verbose_name="Товар", on_delete=models.CASCADE
    )
    buyer = models.ForeignKey(
        Client, verbose_name="Покупатель", on_delete=models.CASCADE
    )
    amount = models.DecimalField(
        "Сумма сделки", max_digits=19, decimal_places=2
    )
    bills = models.ManyToManyField(Bill, through="DealBill")

    def __str__(self):
        return f"{self.product.name}: {self.amount}"

    def get_commission(self):
        """По бизнес логике, клиент оплачивает коммиссионные за сервис"""

        # TODO инжектить отдельно расчет коммиссии в зависимости
        # от типа пользователя(добавить прем юзеров)
        return (
            self.amount
            * (
                settings.COMMISSION_PART[self.product.seller.company.id]
                + self.product.seller.company.vat
            )
            / 100
        )

    def get_proceeds(self):
        """Выручка, это цена продажи за вычетом коммиссионных"""
        return self.amount - self.get_commission()

    def create_bills(self) -> List[Bill]:
        """
        Проведение бизнес транзакций

        первый счет - списание у покупателя полной стоймости
        второй счет - начисление продавцу полной стоймости
        третий счет - списание у продовца коммиссионых
        """
        # TODO Возможно тут есть место для стратегии.

        # первый счет - списание у покупателя
        bill_sell = Bill.objects.create(
            client=self.buyer,
            bill_type=BillType.SELL,
            amount=self.amount,
            vat=self.buyer.vat,
        )

        self.bills.add(bill_sell)

        # второй счет - начисление продавцу
        bill_proceeds = Bill.objects.create(
            client=self.product.seller,
            bill_type=BillType.PROCEEDS,
            amount=self.amount,
            vat=self.buyer.vat,
        )

        self.bills.add(bill_proceeds)

        # третий счет - списание коммиссионых
        bill_commission = Bill.objects.create(
            client=self.product.seller,
            bill_type=BillType.COMMISSION,
            amount=self.get_commission(),
            vat=self.buyer.vat,
        )

        self.bills.add(bill_commission)

        return [bill_sell, bill_proceeds, bill_commission]

    def finalize(self) -> None:
        """финализируем сделку"""
        # TODO send email
        bills: List[Bill] = self.create_bills()

        for bill in bills:
            bill.async_activate()

    def async_finalize(self) -> None:
        """
        асинхронно активируем сделку
        вызываем при создании сделки.
        """
        deal_finalize.delay(deal_id=self.id)


class DealBill(ModelAbstract):
    """связь между сделками и счетами"""

    deal = models.ForeignKey(
        Deal, verbose_name="Сделка", on_delete=models.CASCADE
    )
    bill = models.ForeignKey(
        Bill, verbose_name="Счет", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.deal} - {self.bill}"

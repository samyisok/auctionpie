from __future__ import annotations

from abc import ABC, abstractclassmethod, abstractmethod, abstractproperty
from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from billing.models import Payment


class AbastactPaymentSystemResult(ABC):
    payment_system: Type[AbstractPaymentSystem]

    @abstractmethod
    def is_confirm_avalible(self):
        """ Проверяем доступен ли confirm PS """
        ...

    @abstractproperty
    def confirm_url(self):
        """
        Урл для подтверждения платежа,
        может не существовать для некоторых ПС
        """
        ...

    @abstractproperty
    def is_failed(self):
        """ Платеж не успешен """
        ...


class AbstractPaymentSystem(ABC):
    payment: Payment

    @abstractmethod
    def process_payment(self):
        """ Запускаем обработку платежа """
        ...

    @abstractmethod
    def process_request(self):
        """ обрабатываем внешний """
        ...

    @abstractclassmethod
    def is_confirm_avalible(cls):
        """ Confirming_url доступен ли для этой ПС """
        ...

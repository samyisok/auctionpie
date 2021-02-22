from __future__ import annotations

from abc import ABC, abstractclassmethod, abstractmethod, abstractproperty
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from billing.models import Payment


class AbastactPaymentSystemResult(ABC):
    payment_system: AbstractPaymentSystem

    @abstractproperty
    def is_confirm_avalible(self) -> bool:
        """ Проверяем доступен ли confirm ПС """
        ...

    @abstractproperty
    def is_invoice_avalible(self) -> bool:
        """ некоторые платежные системы могут отдавать инвойс """
        ...

    @abstractmethod
    def get_confirm_url(self) -> str:
        """
        Урл для подтверждения платежа,
        может не существовать для некоторых ПС
        """
        ...

    @abstractmethod
    def get_invoice(self) -> str:
        """
        инвойс в base64
        """
        ...

    @abstractproperty
    def is_failed(self) -> bool:
        """ Платеж не успешен """
        ...

    @abstractproperty
    def is_pending(self) -> bool:
        """ платеж еще выполняется """
        ...

    @abstractproperty
    def is_success(self) -> bool:
        """ платеж успешный """
        ...


class AbstractPaymentSystem(ABC):
    payment: Payment

    @abstractmethod
    def process_payment(self) -> None:
        """ Запускаем обработку платежа """
        ...

    @abstractmethod
    def get_process_payment_result(self) -> AbastactPaymentSystemResult:
        """
        Возвращаем обьект результатов обработки платежа
        так как возможно процесс платежа будет обрабатывать ассинхронно
        """
        ...

    @abstractmethod
    def is_process_payment_result_ready(self) -> bool:
        """
        Проверяем обработали ли платеж
        проверяем по наличию информации в платеже в поле data
        """
        ...

    @abstractmethod
    def process_request(self) -> None:
        """ обрабатываем внешний запрос"""
        ...

    @abstractclassmethod
    def is_confirm_avalible(cls) -> bool:
        """ Confirming_url доступен ли для этой ПС """
        ...

    @abstractclassmethod
    def is_invoice_avalible(cls) -> bool:
        """ инвойс доступен ли для этой ПС """
        ...


class PaymentSystemResult(AbastactPaymentSystemResult):
    """ результат обработки платежа """

    def __init__(
        self,
        payment_system: AbstractPaymentSystem,
        confirm_url: str,
        invoice: str,
        failed: bool,
        pending: bool,
        success: bool,
    ):
        self.payment_system: AbstractPaymentSystem = payment_system
        self.confirm_url: str = confirm_url
        self.invoice: str = invoice
        self.failed: bool = failed
        self.pending: bool = pending
        self.success: bool = success

    @property
    def is_confirm_avalible(self) -> bool:
        return self.payment_system.is_confirm_avalible()

    @property
    def is_invoice_avalible(self) -> bool:
        return self.payment_system.is_invoice_avalible()

    def get_invoice(self) -> str:
        return self.invoice

    def get_confirm_url(self) -> str:
        return self.confirm_url

    @property
    def is_failed(self) -> bool:
        """ Платеж не успешен """
        return self.failed

    @property
    def is_pending(self) -> bool:
        """ платеж ожидает обновления """
        return self.pending

    @property
    def is_success(self) -> bool:
        """ платеж ожидает обновления """
        return self.success

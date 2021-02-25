from typing import TYPE_CHECKING, Type

from django.apps import apps

from core.celery import app

if TYPE_CHECKING:
    from billing.models import Bill, Payment


@app.task()
def bill_activate(bill_id):
    """ активация """
    bill_model: Type[Bill] = apps.get_model("billing", "Bill")
    bill: Bill = bill_model.objects.get(id=bill_id)
    return bill.activate()


@app.task()
def payment_process(payment_id):
    """ Начать процесс обработки платежа """
    payment_model: Type[Payment] = apps.get_model("billing", "Payment")
    payment: Payment = payment_model.objects.get(id=payment_id)
    return payment.process()

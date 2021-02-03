from celery import shared_task
from django.apps import apps


@shared_task
def bill_activate(bill_id):
    """ активация """
    bill_model = apps.get_model("billing", "Bill")
    bill = bill_model.objects.get(id=bill_id)
    return bill.activate()

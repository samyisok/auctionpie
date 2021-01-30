from celery import shared_task


@shared_task
def async_send_email(msg, template):
    # TODO в будущем будем слать почту, а пока так.
    print(msg, template)
    return True

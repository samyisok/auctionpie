from django.db import models
from django.utils import timezone


class ModelAbstract(models.Model):
    cdate = models.DateTimeField("Дата создания", default=timezone.now)
    mdate = models.DateTimeField(
        "Дата изменения",
        auto_now=True,
        auto_now_add=False,
    )

    class Meta:
        abstract = True

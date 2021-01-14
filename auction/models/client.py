from django.db import models


class Client(models.Model):
    FACES = [
        (1, u"Физ лицо"),
        (2, u"Юр лицо"),
        (3, u"ИП"),
        (4, u"Бюджет"),
    ]

    email = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=128)
    cdate = models.DateTimeField(auto_now=False, auto_now_add=True)
    mdate = models.DateTimeField(auto_now=True, auto_now_add=False)
    company_id = models.IntegerField(default=1)
    activated = models.BooleanField(default=False)
    face_id = models.IntegerField(
        choices=FACES,
        default=1,
    )

# Generated by Django 3.1.5 on 2021-01-13 22:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Client",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("email", models.CharField(max_length=128, unique=True)),
                ("password", models.CharField(max_length=128)),
                ("cdate", models.DateTimeField(auto_now_add=True)),
                ("mdate", models.DateTimeField(auto_now=True)),
                ("company_id", models.IntegerField(default=1)),
                ("activated", models.BooleanField(default=False)),
                (
                    "face_id",
                    models.IntegerField(
                        choices=[
                            (1, "Физ лицо"),
                            (2, "Юр лицо"),
                            (3, "ИП"),
                            (4, "Бюджет"),
                        ],
                        default=1,
                    ),
                ),
            ],
        ),
    ]

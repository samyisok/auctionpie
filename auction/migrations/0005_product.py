# Generated by Django 3.1.5 on 2021-01-14 08:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auction", "0004_auto_20210114_0848"),
    ]

    operations = [
        migrations.CreateModel(
            name="Product",
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
                ("name", models.CharField(max_length=128)),
                ("description", models.TextField()),
                ("start_price", models.FloatField()),
                ("buy_price", models.FloatField()),
                ("start_date", models.DateTimeField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "Активный"),
                            ("inactive", "Неактивный"),
                            ("deleted", "Удаленный"),
                            ("sold", "Проданный"),
                            ("canceled", "Отменен"),
                        ],
                        default="inactive",
                        max_length=64,
                    ),
                ),
                ("cdate", models.DateTimeField(auto_now_add=True)),
                ("mdate", models.DateTimeField(auto_now=True)),
                (
                    "seller",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="auction.client",
                    ),
                ),
            ],
        ),
    ]

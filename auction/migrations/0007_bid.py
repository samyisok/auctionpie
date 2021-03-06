# Generated by Django 3.1.5 on 2021-01-14 17:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auction", "0006_product_end_date"),
    ]

    operations = [
        migrations.CreateModel(
            name="Bid",
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
                (
                    "status",
                    models.CharField(
                        choices=[("active", "Active"), ("deleted", "Deleted")],
                        default="active",
                        max_length=32,
                    ),
                ),
                ("price", models.DecimalField(decimal_places=2, max_digits=11)),
                ("cdate", models.DateTimeField(auto_now_add=True)),
                ("mdate", models.DateTimeField(auto_now=True)),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="auction.client",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="auction.product",
                    ),
                ),
            ],
        ),
    ]

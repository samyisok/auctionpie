# Generated by Django 3.1.5 on 2021-01-24 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auction", "0022_auto_20210124_1151"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="status",
            field=models.CharField(
                choices=[
                    ("active", "Активный"),
                    ("inactive", "Не активный"),
                    ("deleted", "Удаленный"),
                    ("sold", "Проданный"),
                    ("canceled", "Отменен"),
                ],
                default="inactive",
                max_length=64,
            ),
        ),
    ]

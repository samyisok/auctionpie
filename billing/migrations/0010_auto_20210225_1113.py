# Generated by Django 3.1.6 on 2021-02-25 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0009_auto_20210221_0510'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='data',
            field=models.JSONField(null=True, verbose_name='Информация от платежной системы'),
        ),
    ]

# Generated by Django 3.1.5 on 2021-01-19 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0002_auto_20210119_0518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='comment',
            field=models.CharField(max_length=128, null=True, verbose_name='Комментарий'),
        ),
    ]

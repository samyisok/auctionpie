# Generated by Django 3.1.6 on 2021-02-21 05:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0008_auto_20210214_2041'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='description',
            field=models.TextField(default='', verbose_name='Описание платежа'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_system',
            field=models.CharField(choices=[('dummy', 'Псевдо платежная система'), ('yoomoney', 'Псевдо платежная система')], default='dummy', max_length=64, verbose_name='Тип платежной системы'),
        ),
    ]

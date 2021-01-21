# Generated by Django 3.1.5 on 2021-01-21 14:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0005_auto_20210121_0941'),
        ('auction', '0019_insert_company'),
    ]

    operations = [
        migrations.CreateModel(
            name='Deal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cdate', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата создания')),
                ('mdate', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=19, verbose_name='Сумма сделки')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='bid',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=19),
        ),
        migrations.AlterField(
            model_name='product',
            name='start_price',
            field=models.DecimalField(decimal_places=2, max_digits=19),
        ),
        migrations.CreateModel(
            name='DealBill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cdate', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата создания')),
                ('mdate', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('bill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.bill', verbose_name='Счет')),
                ('deal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auction.deal', verbose_name='Сделка')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='deal',
            name='bills',
            field=models.ManyToManyField(through='auction.DealBill', to='billing.Bill'),
        ),
        migrations.AddField(
            model_name='deal',
            name='buyer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Покупатель'),
        ),
        migrations.AddField(
            model_name='deal',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auction.product', verbose_name='Товар'),
        ),
    ]

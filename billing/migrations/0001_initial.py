# Generated by Django 3.1.5 on 2021-01-18 16:11

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tnx_type', models.CharField(choices=[('deposit', 'Зачисление на аккаунт пользователя'), ('expesne', 'Списание за услуги с аккаунта пользователя'), ('withdraw', 'Вывод средств с аккаунта пользователя во вне'), ('cancellation ', 'Пополнение счета, средствами с отмены списания')], max_length=32, verbose_name='Тип транзакции')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=19, verbose_name='Сумма операции')),
                ('cdate', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата создания')),
                ('mdate', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('comment', models.CharField(max_length=128, verbose_name='Комментарий')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Владелец транзакции')),
            ],
        ),
    ]

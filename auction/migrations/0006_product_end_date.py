# Generated by Django 3.1.5 on 2021-01-14 09:58

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0005_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='end_date',
            field=models.TimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
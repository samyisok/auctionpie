# Generated by Django 3.1.5 on 2021-01-16 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0015_remove_client_is_confirmed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='end_date',
            field=models.DateTimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='start_date',
            field=models.DateTimeField(blank=True),
        ),
    ]
# Generated by Django 3.1.5 on 2021-01-16 03:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0014_client_is_admin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='is_confirmed',
        ),
    ]

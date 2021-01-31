# Generated by Django 3.1.5 on 2021-01-14 08:48

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auction", "0003_auto_20210114_0811"),
    ]

    operations = [
        migrations.AddField(
            model_name="clientdata",
            name="cdate",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="clientdata",
            name="mdate",
            field=models.DateTimeField(auto_now=True),
        ),
    ]

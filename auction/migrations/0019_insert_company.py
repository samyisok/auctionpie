from django.db import migrations


def insert_first_company(apps, schema_editor):
    Company = apps.get_model("auction", "Company")
    company = Company(
        name="ООО Тестовая Компания",
        address="Тестовая улица",
        inn="1234567890",
        vat=20,
        is_vat_active=True,
    )
    company.save()


class Migration(migrations.Migration):

    dependencies = [
        ("auction", "0018_company"),
    ]

    operations = [migrations.RunPython(insert_first_company)]

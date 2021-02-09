from django.test import TestCase

from auction.models import Company


class ModelsCompanyTestCase(TestCase):
    """product model test"""

    def test_str_first_company(self):
        """ should __str__ first company """
        company: Company = Company.objects.get(id=1)
        self.assertEqual(str(company), "ООО Тестовая Компания")

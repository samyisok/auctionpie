from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

email = "emailfortest@test.ru"
password = "password"
email_seller = "seller@test.ru"
password_seller = "password"
amount = Decimal("12.34")
amount_100 = Decimal("100.00")
product_params = {
    "name": "product name",
    "description": "product desc",
    "start_price": Decimal(10),
    "buy_price": Decimal(20),
    "start_date": timezone.now(),
    "end_date": timezone.now() + timedelta(7),
}

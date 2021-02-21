# some business logic conf
import os

DEFAULT_COMPANY = 1
COMMISSION_PART = {DEFAULT_COMPANY: 10}  # percentage for company 1

PAYMENT_RETURN_URL = "http//localhost:8000"

YOOMONEY = "yoomoney"

PAYMENT_SYSTEMS = {
    YOOMONEY: {
        "key": os.environ.get("YOOMONEY_KEY"),
        "shop_id": os.environ.get("YOOMONEY_SHOPID"),
        "active": True,
        "return_url": PAYMENT_RETURN_URL,
    }
}

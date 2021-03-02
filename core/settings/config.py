# some business logic conf
import os
from typing import Dict, Union

DEFAULT_COMPANY: int = 1
COMMISSION_PART: Dict[int, int] = {
    DEFAULT_COMPANY: 10
}  # percentage for company 1

PAYMENT_RETURN_URL: str = "http//localhost:8000"

YOOMONEY: str = "yoomoney"

PAYMENT_SYSTEMS: Dict[str, Dict[str, Union[str, bool, None]]] = {
    YOOMONEY: {
        "key": os.environ.get("YOOMONEY_KEY"),
        "shop_id": os.environ.get("YOOMONEY_SHOPID"),
        "active": True,
        "return_url": PAYMENT_RETURN_URL,
    }
}

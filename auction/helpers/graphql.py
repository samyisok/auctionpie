"""
Методы для вызова из graphql
"""
from auction.models import Product


def create_new_product(
    client, name, description, start_price, buy_price, start_date, end_date
):
    product = Product(
        seller=client,
        name=name,
        description=description,
        start_price=start_price,
        buy_price=buy_price,
        start_date=start_date,
        end_date=end_date,
    )

    product.save()
    return product


def update_product():
    pass


def cancel_product():
    pass


def make_bid():
    pass

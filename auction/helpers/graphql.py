"""
Методы для вызова из graphql
"""
from auction.models import Bid, Product
from auction.structures.graphql import BidInput, ProductInput


def create_new_product(product_input: ProductInput) -> Product:
    product = Product(
        seller=product_input.seller,
        name=product_input.name,
        description=product_input.description,
        start_price=product_input.start_price,
        buy_price=product_input.buy_price,
        start_date=product_input.start_date,
        end_date=product_input.end_date,
    )

    product.save()
    product.async_send_email(type="new")
    return product


def update_product():
    pass


def cancel_product():
    pass


def create_bid(bid_input: BidInput) -> Bid:
    product = Product.objects.get(id=bid_input.product_id)

    bid = Bid(
        client=bid_input.client,
        price=bid_input.price,
        product=product,
    )

    bid.save()
    bid.post_save()
    return bid

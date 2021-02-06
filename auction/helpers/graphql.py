"""
Методы для вызова из graphql
"""
from auction.models import Bid, Product
from auction.structures.graphql import (BidInput, ProductDeleteInput,
                                        ProductInput, ProductUpdateInput)
from core.errors import CodeError


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


def update_product(product_update_input: ProductUpdateInput) -> Product:
    product: Product = Product.objects.get(id=product_update_input.product_id)

    if product_update_input.seller != product.seller:
        raise CodeError.WRONG_USER.exception

    changes: dict = {
        key: value
        for (key, value) in product_update_input.dict().items()
        if key not in ["seller", "product_id"] and value is not None
    }

    if not changes:
        raise CodeError.NO_CHANGES_SPECIFIED.exception

    for (key, value) in changes.items():
        setattr(product, key, value)

    product.save()

    return product


def activate_product():
    pass


def delete_product(product_delete_input: ProductDeleteInput):
    product = Product.objects.get(id=product_delete_input.product_id)
    product.delete()
    return product


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

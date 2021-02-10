"""
Методы для вызова из graphql
"""
from typing import List

from django.core.paginator import Paginator

from auction.models import Bid, Product
from auction.structures.graphql import (BidInput, PageListInput,
                                        ProductActionInput, ProductInput,
                                        ProductUpdateInput)
from core.errors import CodeError


def create_new_product(product_input: ProductInput) -> Product:
    """ создание товара на аукцион """
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
    """ обновление данных по товару """
    product: Product = Product.objects.get(id=product_update_input.product_id)

    if product_update_input.seller != product.seller:
        raise CodeError.WRONG_CLIENT.exception

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


def activate_product(product_action_input: ProductActionInput):
    """ Выставление продукта на аукцион """
    product: Product = Product.objects.get(id=product_action_input.product_id)

    if product_action_input.seller != product.seller:
        raise CodeError.WRONG_CLIENT.exception

    product.activate()
    return product


def delete_product(product_action_input: ProductActionInput):
    """ Удаление продукта """
    product: Product = Product.objects.get(id=product_action_input.product_id)

    if product_action_input.seller != product.seller:
        raise CodeError.WRONG_CLIENT.exception

    product.delete()
    return product


def create_bid(bid_input: BidInput) -> Bid:
    """ Выставление новой ставки по товару """
    product = Product.objects.get(id=bid_input.product_id)

    bid = Bid(
        client=bid_input.client,
        price=bid_input.price,
        product=product,
    )

    bid.save()
    bid.post_save()
    return bid


def get_product_list(input: PageListInput) -> List:
    """
    получаем список продуктов на аукционе
    """
    products: List[Product] = Product.objects.all().order_by("id")
    paginator: Paginator = Paginator(products, input.page_size)
    return paginator.page(input.page)

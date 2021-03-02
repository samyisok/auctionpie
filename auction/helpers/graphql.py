"""
Методы для вызова из graphql
"""
import functools
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Union

from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Page, Paginator

from auction.models import Bid, Product
from auction.structures.graphql import (
    BidInput,
    IdInput,
    PageListInput,
    ProductActionInput,
    ProductInput,
    ProductUpdateInput,
)
from core.errors import CodeError

if TYPE_CHECKING:
    from datetime import datetime

    from django.db.models import Manager


def catch_product_not_found(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except ObjectDoesNotExist as exc:
            if (
                isinstance(exc, ObjectDoesNotExist)
                and exc.args[0] == "Product matching query does not exist."
            ):
                raise CodeError.PRODUCT_NOT_FOUND.exception
            else:
                raise exc

    return wrapper


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


@catch_product_not_found
def update_product(product_update_input: ProductUpdateInput) -> Product:
    """ обновление данных по товару """
    product: Product = Product.objects.get(id=product_update_input.product_id)

    if product_update_input.seller != product.seller:
        raise CodeError.WRONG_CLIENT.exception

    changes: Dict[str, Union[Optional[str], Optional[datetime]]] = {
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


@catch_product_not_found
def activate_product(product_action_input: ProductActionInput) -> Product:
    """ Выставление продукта на аукцион """
    product: Product = Product.objects.get(id=product_action_input.product_id)

    if product_action_input.seller != product.seller:
        raise CodeError.WRONG_CLIENT.exception

    product.activate()
    return product


@catch_product_not_found
def delete_product(product_action_input: ProductActionInput) -> Product:
    """ Удаление продукта """
    product: Product = Product.objects.get(id=product_action_input.product_id)

    if product_action_input.seller != product.seller:
        raise CodeError.WRONG_CLIENT.exception

    product.delete_product()
    return product


@catch_product_not_found
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


def get_product_list(input: PageListInput) -> Page:
    """
    получаем список продуктов на аукционе
    """
    products: Manager[Product] = Product.objects.all().order_by("id")
    paginator: Paginator = Paginator(products, input.page_size)
    return paginator.page(input.page)


@catch_product_not_found
def get_product(input: IdInput) -> Product:
    """
    получаем конкретный продукт
    """
    return Product.objects.get(id=input.id)


@catch_product_not_found
def get_product_price(input: IdInput) -> Decimal:
    """
    получаем цену продукта
    """
    return Product.objects.get(id=input.id).get_final_bid_price()

Django Graphql Auction Backend(with celery)
===========================================

Суть эксперемента универсальный бекенд для аукциона товаров с отдельным учетом движения средств и платежей.
Для фронта будет предоставлен API через graphql.

Graphq list of queries and mutations:
=====================================
Mutations:
----------
 - Register: Register user with fields defined in the settings.
 - VerifyAccount: Verify user account.
 - ObtainJSONWebToken: Obtain JSON web token for given user.
 - VerifyToken: Same as `grapgql_jwt` implementation, with standard output.
 - RefreshToken: Same as `grapgql_jwt` implementation, with standard output.
 - RevokeToken: Same as `grapgql_jwt` implementation, with standard output.
 - CreateProduct: Создание и выставление продукта на аукцион.
 - CreateBid: Создание ставки на товар
 - DeleteProduct: Отмена продукта
 - UpdateProduct: Изменение продукта
 - ActivateProduct: Активация продукта клиента(выставление на аукцион)
Queries:
--------
 - balance: Получаем баланс клиента
 - productList: Получаем список продуктов на аукционе
 - product: Получаем конкретный продукт
 - productPrice: Получаем цену конкретного продукта

Test coverage
=============
::

  Name                             Stmts   Miss Branch BrPart  Cover
  ------------------------------------------------------------------
  auction/__init__.py                  0      0      0      0   100%
  auction/admin.py                    52     11      6      0    74%
  auction/helpers/__init__.py          0      0      0      0   100%
  auction/helpers/graphql.py          48      0     12      0   100%
  auction/models/__init__.py           6      0      0      0   100%
  auction/models/base.py               7      0      0      0   100%
  auction/models/bid.py               38      0      2      0   100%
  auction/models/client.py            74      0      2      0   100%
  auction/models/client_data.py       17      0      0      0   100%
  auction/models/company.py           11      0      0      0   100%
  auction/models/deal.py              38      0      2      0   100%
  auction/models/product.py           98      0     22      0   100%
  auction/mutations.py                67     20      0      0    70%
  auction/schema.py                   25      0      0      0   100%
  auction/structures/__init__.py       0      0      0      0   100%
  auction/structures/graphql.py       86     10     20     10    81%
  auction/tasks.py                    29      0      2      0   100%
  auction/types.py                    15      0      0      0   100%
  billing/__init__.py                  0      0      0      0   100%
  billing/admin.py                     4      0      0      0   100%
  billing/helpers/__init__.py          0      0      0      0   100%
  billing/helpers/graphql.py           5      0      0      0   100%
  billing/meta.py                     15      0      0      0   100%
  billing/models/__init__.py           2      0      0      0   100%
  billing/models/bill.py              33      0      0      0   100%
  billing/models/transaction.py       53      0     10      0   100%
  billing/schema.py                   12      3      0      0    75%
  billing/strategies.py               51      0      8      0   100%
  billing/structures/__init__.py       0      0      0      0   100%
  billing/structures/graphql.py        7      0      0      0   100%
  billing/tasks.py                     7      0      0      0   100%
  core/__init__.py                     2      0      0      0   100%
  core/celery.py                       7      0      0      0   100%
  core/errors.py                      27      0      0      0   100%
  core/schema.py                      17      0      0      0   100%
  ------------------------------------------------------------------
  TOTAL                              853     44     86     10    94%

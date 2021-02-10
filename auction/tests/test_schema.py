import json
from typing import Dict

from graphene_django.utils.testing import GraphQLTestCase

from auction.models import Client, Product
from auction.tests.fixures import email_seller, product_params


class QueriesProductTestCase(GraphQLTestCase):
    def setUp(self):
        self.seller: Client = Client.objects.create_user(
            email_seller, "password"
        )
        self.product_params: Dict = {"seller": self.seller, **product_params}
        self.product: Product = Product.objects.create(**self.product_params)

    def test_product_list(self):

        response = self.query(
            """
            query {
                productList {
                    id
                    name
                    description
                }
            }
            """,
            variables={"page": 1, "pageSize": 10},
        )

        content = json.loads(response.content)
        print(content)
        # This validates the status code and if you get errors
        self.assertResponseNoErrors(response)

        # Add some more asserts if you like
        ...

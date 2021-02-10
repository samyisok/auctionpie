import json
from typing import Dict

from graphene_django.utils.testing import GraphQLTestCase

from auction.models import Client, Product
from auction.tests.fixures import email_seller, product_params


class QueriesProductListTestCase(GraphQLTestCase):
    def setUp(self):
        self.seller: Client = Client.objects.create_user(
            email_seller, "password"
        )
        self.product_params: Dict = {"seller": self.seller, **product_params}
        self.product: Product = Product.objects.create(**self.product_params)

    def test_product_list(self):
        """ should get list of products """
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
        )

        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        data = content["data"]["productList"]
        expected = [
            {
                "id": str(self.product.id),
                "name": self.product_params["name"],
                "description": self.product_params["description"],
            }
        ]
        self.assertListEqual(data, expected)


class QueriesProductTestCase(GraphQLTestCase):
    def setUp(self):
        self.seller: Client = Client.objects.create_user(
            email_seller, "password"
        )
        self.product_params: Dict = {"seller": self.seller, **product_params}
        self.product: Product = Product.objects.create(**self.product_params)

    def test_product(self):
        """ should get a concrete product"""
        response = self.query(
            """
            query product($id: ID!){
                product(id: $id){
                    id
                    name
                    description
                }
            }
            """,
            op_name="product",
            variables={"id": self.product.id},
        )

        content = json.loads(response.content)
        self.assertResponseNoErrors(response)
        data = content["data"]["product"]
        expected = {
            "id": str(self.product.id),
            "name": self.product_params["name"],
            "description": self.product_params["description"],
        }

        self.assertDictEqual(data, expected)
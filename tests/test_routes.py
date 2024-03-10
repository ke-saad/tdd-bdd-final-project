import os
import logging
from decimal import Decimal
from unittest import TestCase
from service import app
from service.common import status
from service.models import db, init_db, Product
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)
BASE_URL = "/products"


class TestProductRoutes(TestCase):
    """Product Service tests"""

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        db.session.close()

    def setUp(self):
        self.client = app.test_client()
        db.session.query(Product).delete()
        db.session.commit()

    def tearDown(self):
        db.session.remove()

    def _create_products(self, count: int = 1) -> list:
        """Factory method to create products in bulk"""
        products = []
        for _ in range(count):
            test_product = ProductFactory()
            response = self.client.post(BASE_URL, json=test_product.serialize())
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test product"
            )
            new_product = response.get_json()
            test_product.id = new_product["id"]
            products.append(test_product)
        return products

    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b"Product Catalog Administration", response.data)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data['message'], 'OK')

    def test_create_product(self):
        test_product = ProductFactory()
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_product = response.get_json()
        self.assertEqual(new_product["name"], test_product.name)
        self.assertEqual(new_product["description"], test_product.description)
        self.assertEqual(Decimal(new_product["price"]), test_product.price)
        self.assertEqual(new_product["available"], test_product.available)
        self.assertEqual(new_product["category"], test_product.category.name)

    def test_create_product_with_no_name(self):
        product = self._create_products()[0]
        new_product = product.serialize()
        del new_product["name"]
        response = self.client.post(BASE_URL, json=new_product)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_no_content_type(self):
        response = self.client.post(BASE_URL, data="bad data")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_product_wrong_content_type(self):
        response = self.client.post(BASE_URL, data={}, content_type="plain/text")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_get_product(self):
        test_product = self._create_products(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_product.name)

    def test_get_product_not_found(self):
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])

    def test_update_product(self):
        test_product = self._create_products(1)[0]
        test_product.name = "Updated Product Name"
        response = self.client.put(f"{BASE_URL}/{test_product.id}", json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_product = response.get_json()
        self.assertEqual(updated_product["name"], test_product.name)

    def test_delete_product(self):
        test_product = self._create_products(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Ensure the product is deleted
        response = self.client.get(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_products(self):
        num_products = 5
        products = self._create_products(num_products)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), num_products)

    def test_list_products_by_name(self):
        product_name = "Test Product"
        num_products = 3
        products = self._create_products(num_products)
        # Update the names of the products to match product_name
        for product in products:
            product.name = product_name
            self.client.put(f"{BASE_URL}/{product.id}", json=product.serialize())
        # Retrieve the products by name
        response = self.client.get(f"{BASE_URL}?name={product_name}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), num_products)

    def test_list_products_by_category(self):
        product_category = "Test Category"
        num_products = 3
        products = self._create_products(num_products)
        # Update the category of the products to match product_category
        for product in products:
            product.category = product_category
            self.client.put(f"{BASE_URL}/{product.id}", json=product.serialize())
        # Retrieve the products by category
        response = self.client.get(f"{BASE_URL}?category={product_category}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), num_products)

    def test_list_products_by_availability(self):
        product_availability = True
        num_products = 3
        # Create products with the given availability
        for _ in range(num_products):
            product = ProductFactory(available=product_availability)
            self.client.post(BASE_URL, json=product.serialize())
        # Retrieve the products by availability
        response = self.client.get(f"{BASE_URL}?available={product_availability}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), num_products)


    def get_product_count(self):
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        return len(data)

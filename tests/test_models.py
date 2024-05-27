# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #

    def test_read_product(self):
        """It should read a product"""
        product = ProductFactory()
        logging.debug("Reading product %s", product.name)
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        product_found = Product.find(product.id)

        self.assertEqual(product_found.id, product.id)
        self.assertEqual(product_found.name, product.name)
        self.assertEqual(product_found.category, product.category)
        self.assertEqual(product_found.description, product.description)
        self.assertEqual(product_found.price, product.price)

    def test_update_product(self):
        """It should update a product"""

        product = ProductFactory()
        logging.debug("Reading product %s ", product.name)
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        logging.debug("Reading product again %s ", product.name)

        product.description = "New description of product"
        old_id = product.id
        product.update()
        logging.debug("Updated product to description %s ",  product.description)

        self.assertEqual(product.id, old_id)
        self.assertEqual(product.description, "New description of product")

        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, old_id)
        self.assertEqual(products[0].description, "New description of product")

    def test_delete_product(self):
        """It should delete a product"""

        # create product
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)

        # assert only one product present
        products = Product.all()
        self.assertEqual(len(products), 1)

        # delete product
        logging.debug("Deleting product {product.name}")
        product.delete()
        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_list_all_products(self):
        """It should list all products"""

        # make sure no products exist yet
        products = Product.all()
        logging.debug("Length of products %s ", len(products))
        self.assertEqual(products, [])

        # create 5 products
        for _ in range(5):
            new_product = ProductFactory()
            new_product.create()
        logging.debug("Length of products %s ", len(Product.all()))
        self.assertEqual(5, len(Product.all()))

    def test_find_product_by_name(self):
        """It should find a product by name"""
        # create 5 products
        products = ProductFactory.create_batch(5)

        for product in products:
            product.create()

        # retrive all 5 products
        products_name = products[0].name

        # get counts
        count = len([product for product in products if product.name == products_name])
        # assert
        found = Product.find_by_name(products_name)
        logging.debug("Product found: %s ", found)
        self.assertEqual(count, found.count())
        for product in found:
            self.assertEqual(product.name, products_name)

    def test_find_product_by_category(self):
        """It should find a product by category"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        first_product_category = products[0].category

        count = len([product for product in products if product.category == first_product_category])

        found_products_cat = Product.find_by_category(first_product_category)

        self.assertEqual(found_products_cat.count(), count)
        for product in found_products_cat:
            self.assertEqual(product.category, first_product_category)

    def test_find_product_by_availability(self):
        """It should find a product by availability"""

        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        first_product_availability = products[0].available

        count = len([product for product in products if product.available == first_product_availability])

        found_products_avail = Product.find_by_availability(first_product_availability)

        self.assertEqual(found_products_avail.count(), count)
        for product in found_products_avail:
            self.assertEqual(product.available, first_product_availability)

    def test_find_product_by_price(self):
        """It should find a product by price"""

        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        first_product_price = products[0].price

        count = len([product for product in products if product.price == first_product_price])

        found_products_price = Product.find_by_price(first_product_price)

        self.assertEqual(found_products_price.count(), count)
        for product in found_products_price:
            self.assertEqual(product.price, first_product_price)

    def test_find_product_by_id(self):
        """It should find a product by id"""

        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        first_product_id = products[0].id

        found_products_id = Product.find(first_product_id).id

        self.assertEqual(found_products_id, Product.all()[0].id)

    def test_serialize_product(self):
        """It should serialize product to dict"""
        product = ProductFactory()
        product.create()
        self.assertIsNotNone(product.id)

        dict_product = product.serialize()
        self.assertIsInstance(dict_product, dict)

    def test_repr(self):
        """It should print magic fnctn"""
        product = ProductFactory()
        product.create()
        self.assertIsNotNone(product.id)

        self.assertEqual(str(product), f"<Product {product.name} id=[{product.id}]>")

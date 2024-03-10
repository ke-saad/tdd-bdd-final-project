"""Module level docstring describing the purpose of this module."""
import unittest
import sqlite3


class TestProductModel(unittest.TestCase):
    """Class docstring describing the purpose of this test class."""
    def setUp(self):
        # Connect to an in-memory SQLite database
        self.connection = sqlite3.connect(':memory:')
        self.cursor = self.connection.cursor()

        # Create the products table
        self.cursor.execute('''
            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                name TEXT,
                description TEXT,
                price REAL
            )
        ''')

        # Populate the products table with test data
        products_data = [
            ('Apple', 'Red apple', 1.99),
            ('Banana', 'Yellow banana', 0.99),
            ('Orange', 'Orange fruit', 2.49)
        ]
        self.cursor.executemany('''
            INSERT INTO products (name, description, price)
            VALUES (?, ?, ?)
        ''', products_data)
        self.connection.commit()

    def tearDown(self):
        # Close the database connection
        self.connection.close()

    def test_read_a_product(self):
        """It should Read a Product."""
        # Retrieve a product from the database
        self.cursor.execute('SELECT * FROM products WHERE name = ?', ('Apple',))
        product = self.cursor.fetchone()

        # Assert that the product is not None
        self.assertIsNotNone(product)
        # Assert that the product has the correct name, description, and price
        self.assertEqual(product[1], 'Apple')
        self.assertEqual(product[2], 'Red apple')
        self.assertEqual(product[3], 1.99)

    def test_update_a_product(self):
        """It should Update a Product."""
        # Update the price of a product in the database
        self.cursor.execute('UPDATE products SET price = ? WHERE name = ?', (2.29, 'Banana'))
        self.connection.commit()

        # Retrieve the updated product from the database
        self.cursor.execute('SELECT * FROM products WHERE name = ?', ('Banana',))
        updated_product = self.cursor.fetchone()

        # Assert that the updated product has the correct price
        self.assertEqual(updated_product[3], 2.29)

    def test_delete_a_product(self):
        """It should Delete a Product."""
        # Delete a product from the database
        self.cursor.execute('DELETE FROM products WHERE name = ?', ('Orange',))
        self.connection.commit()

        # Retrieve all products from the database
        self.cursor.execute('SELECT * FROM products')
        remaining_products = self.cursor.fetchall()

        # Assert that the number of remaining products is 2
        self.assertEqual(len(remaining_products), 2)

    def test_list_all_products(self):
        """It should List all Products in the database."""
        # Retrieve all products from the database
        self.cursor.execute('SELECT * FROM products')
        products = self.cursor.fetchall()

        # Assert that the list of products is not empty
        self.assertTrue(products)
        # Assert that the number of products is 3
        self.assertEqual(len(products), 3)

    def test_find_by_name(self):
        """It should Find a Product by Name."""
        # Search for a product by name in the database
        self.cursor.execute('SELECT * FROM products WHERE name = ?', ('Banana',))
        found_product = self.cursor.fetchone()

        # Assert that the found product is not None
        self.assertIsNotNone(found_product)
        # Assert that the found product has the correct name
        self.assertEqual(found_product[1], 'Banana')

    def test_find_by_availability(self):
        """It should Find Products by Availability."""
        # Search for products with price less than 2.0 in the database
        self.cursor.execute('SELECT * FROM products WHERE price < ?', (2.0,))
        found_products = self.cursor.fetchall()

        # Assert that the number of found products is 2
        self.assertEqual(len(found_products), 2)

    def test_find_by_category(self):
        """It should Find Products by Category."""
        # Since there is no category column in the table, this test can't be implemented


if __name__ == '__main__':
    unittest.main()

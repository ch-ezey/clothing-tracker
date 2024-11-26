import unittest
from db.database import setup_database, store_in_db

class TestDatabase(unittest.TestCase):

    def setUp(self):
        """Setup an in-memory database for testing."""
        self.connection = setup_database(test_mode=True)

    def tearDown(self):
        """Close the database connection after each test."""
        self.connection.close()

    def test_store_in_db(self):
        """Test storing items in the database."""
        items = [
            {"unique_id": "123-Size 14", "id": 123, "name": "Test Product", "price": 50.0, "size": "Size 14",
             "category": "Shoes", "url": "http://example.com", "image_url": "http://example.com/image.jpg",
             "availability": "In Stock"}
        ]
        store_in_db(items, self.connection)

        # Verify the item was stored
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM items WHERE unique_id = ?", ("123-Size 14",))
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[1], 123)  # Check ID
        self.assertEqual(row[2], "Test Product")  # Check Name

if __name__ == "__main__":
    unittest.main()

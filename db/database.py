import sqlite3

def setup_database(test_mode=False):
    """
    Sets up the SQLite database for storing product data.
    If test_mode is True, an in-memory database is used.
    """
    db_name = ":memory:" if test_mode else "clothing.db"
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            unique_id TEXT PRIMARY KEY,
            id INTEGER,
            name TEXT,
            price REAL,
            size TEXT,
            category TEXT,
            url TEXT,
            image_url TEXT,
            availability TEXT
        )
    """)
    connection.commit()
    return connection


def store_in_db(items, connection):
    """
    Stores or updates product data in the SQLite database.
    """
    cursor = connection.cursor()
    cursor.executemany("""
        INSERT INTO items (unique_id, id, name, price, size, category, url, image_url, availability)
        VALUES (:unique_id, :id, :name, :price, :size, :category, :url, :image_url, :availability)
        ON CONFLICT(unique_id) DO UPDATE SET
            name=excluded.name,
            price=excluded.price,
            size=excluded.size,
            category=excluded.category,
            url=excluded.url,
            image_url=excluded.image_url,
            availability=excluded.availability
    """, items)
    connection.commit()

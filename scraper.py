import requests
import sqlite3
from time import sleep

# =====================
# DATABASE FUNCTIONS
# =====================

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
            unique_id TEXT PRIMARY KEY, -- Unique identifier (id + size)
            id INTEGER,                -- Original product ID
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
    On conflict (duplicate unique_id), updates the existing record.
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

# =====================
# API AND DATA PROCESSING
# =====================

def fetch_asos_data(category_id, size_code, offset=0, limit=72):
    """
    Fetches product data from the ASOS API for a specific category and size.
    Handles pagination through offset.
    """
    url = f"https://www.asos.com/api/product/search/v2/categories/{category_id}"
    params = {
        "offset": offset,
        "includeNonPurchasableTypes": "restocking",
        "store": "COM",
        "lang": "en-GB",
        "currency": "GBP",
        "rowlength": "2",
        "channel": "mobile-web",
        "country": "GB",
        "keyStoreDataversion": "mhabj1f-41",
        "advertisementsPartnerId": "100712",
        "advertisementsOptInConsent": "false",
        "limit": limit,
        "size": size_code,  # Size code for filtering
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    }
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def parse_asos_data(json_data, size, category_name):
    """
    Parses the JSON response from ASOS API and formats data.
    Adds a unique identifier by combining item ID and size.
    """
    items = []
    for product in json_data.get("products", []):
        item = {
            # "unique_id": f"{product.get('id')}",  # Combine ID and size for uniqueness
            "unique_id": f"{product.get('id')}-{size}",  # Combine ID and size for uniqueness
            "id": product.get("id"),
            "name": product.get("name"),
            "price": product.get("price", {}).get("current", {}).get("value"),
            "size": size,  # Store size as a single value
            "category": category_name,
            "url": f"https://www.asos.com/{product.get('url')}",
            "image_url": product.get("imageUrl"),
            "availability": "In Stock",
        }
        items.append(item)
    return items

# =====================
# HELPER FUNCTIONS
# =====================

def get_size_codes(sizes):
    """
    Converts human-readable sizes to API size codes using the size map.
    """
    size_codes = []
    for size in sizes:
        if size in SIZE_CODE_MAP:
            size_codes.append(SIZE_CODE_MAP[size])
        else:
            print(f"Warning: Size '{size}' not found in size map.")
    return size_codes


def get_category_id(category_name):
    """
    Converts human-readable category names to API category IDs using the category map.
    """
    if category_name in CATEGORY_ID_MAP:
        return CATEGORY_ID_MAP[category_name]
    else:
        print(f"Warning: Category '{category_name}' not found in category map.")
        return None

# =====================
# MAIN FETCH FUNCTION
# =====================

def fetch_all_pages_with_size(category_name, sizes=None, limit=72, connection=None):
    """
    Fetches all products for a given category and size filters, handling pagination.
    Stores results in the database if a connection is provided.
    """
    # Get category ID from human-readable name
    category_id = get_category_id(category_name)
    if not category_id:
        print("Invalid category. Exiting.")
        return []

    # Convert human-readable sizes to API size codes
    size_codes = get_size_codes(sizes) if sizes else None
    all_items = []

    for size, size_code in zip(sizes, size_codes):
        offset = 0
        while True:
            print(f"Fetching data for category '{category_name}', size '{size}', offset {offset}...")
            data = fetch_asos_data(category_id, size_code=size_code, offset=offset, limit=limit)
            if not data or not data.get("products"):
                print(f"No more products found for size '{size}'. Stopping pagination.")
                break

            # Parse data into structured format
            items = parse_asos_data(data, size, category_name)
            all_items.extend(items)

            # Store data in database if connection is provided
            if connection:
                store_in_db(items, connection)

            print(f"Stored {len(items)} items for size '{size}' from offset {offset}.")
            offset += limit
            sleep(1)  # Rate-limiting to avoid being blocked
    return all_items

# =====================
# CONSTANTS
# =====================

SIZE_CODE_MAP = {
    "2XL": 4529,
    "W38 L36": 1583,
    "Size 14": 112
}

CATEGORY_ID_MAP = {
    "Tall": 20753,
    "Jeans": 4208,
    "Trousers": 4910,
    "Shoes": 4209

}

# =====================
# MAIN FUNCTION
# =====================

if __name__ == "__main__":
    test_mode = True
    connection = setup_database(test_mode=test_mode)
    try:
        category_name = "Shoes"  # Human-readable category name
        sizes = ["Size 14"]  # Human-readable sizes
        print("Starting data fetch with category and size filters...")
        all_items = fetch_all_pages_with_size(category_name, sizes=sizes, connection=connection)

        # If in test mode, print a sample of the data
        if test_mode:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM items LIMIT 5")
            rows = cursor.fetchall()
            print("Sample data from in-memory database:")
            for row in rows:
                print(row)
    finally:
        connection.close()
        print("Database closed.")

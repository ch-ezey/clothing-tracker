import requests
from time import sleep
from db.database import store_in_db

# ASOS-specific mappings
SIZE_CODE_MAP = {
    "2XL": 4529,
    "3XL": 4531,
    "W38 L36": 1583,
    "W38 L36": 1584,
    "Size 14": 112
}

CATEGORY_ID_MAP = {
    "Tall": 20753,
    "Jeans": 4208,
    "Trousers": 4910,
    "Shoes": 4209,
    "Jumpers": 7617
}

def fetch_asos_data(category_id, size_code, offset=0, limit=72):
    """
    Fetches product data from the ASOS API for a specific category and size.
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
        "size": size_code,
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
    """
    items = []
    for product in json_data.get("products", []):
        item = {
            "unique_id": f"{product.get('id')}-{size}",
            "id": product.get("id"),
            "name": product.get("name"),
            "price": product.get("price", {}).get("current", {}).get("value"),
            "size": size,
            "category": category_name,
            "url": f"https://www.asos.com/{product.get('url')}",
            "image_url": product.get("imageUrl"),
            "availability": "In Stock",
        }
        items.append(item)
    return items


def fetch_all_pages_with_size(category_name, sizes=None, limit=72, connection=None):
    """
    Fetches all products for a given category and size filters, handling pagination.
    """
    category_id = CATEGORY_ID_MAP.get(category_name)
    if not category_id:
        print(f"Category '{category_name}' not found in ASOS category map.")
        return []

    size_codes = [SIZE_CODE_MAP.get(size) for size in sizes if size in SIZE_CODE_MAP]
    if not size_codes:
        print(f"No valid size codes found for sizes: {sizes}.")
        return []

    all_items = []
    for size, size_code in zip(sizes, size_codes):
        offset = 0
        while True:
            print(f"Fetching data for category '{category_name}', size '{size}', offset {offset}...")
            data = fetch_asos_data(category_id, size_code=size_code, offset=offset, limit=limit)
            if not data or not data.get("products"):
                print(f"No more products found for size '{size}'. Stopping pagination.")
                break

            items = parse_asos_data(data, size, category_name)
            all_items.extend(items)

            if connection:
                store_in_db(items, connection)

            offset += limit
            sleep(1)
    return all_items


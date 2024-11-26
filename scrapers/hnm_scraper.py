import requests
from db.database import store_in_db

def fetch_hnm_data(category_id, size_filter=None, page=1, page_size=36):
    """
    Fetches product data from H&M API for a specific category and optional size filter.
    Handles pagination through page numbers.
    """
    url = "https://api.hm.com/search-services/v1/en_GB/listing/resultpage"
    params = {
        "pageSource": "PLP",
        "page": page,
        "sort": "RELEVANCE",
        "pageId": f"/men/shop-by-product/{category_id}",
        "page-size": page_size,
        "categoryId": category_id,
        "filters": "sale:false||oldSale:false",
        "touchPoint": "DESKTOP",
        "skipStockCheck": "false",
    }

    if size_filter:
        params["facets"] = f"sizes:{size_filter}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from H&M: {e}")
        return None


def parse_hnm_data(json_data, size, category_name):
    """
    Parses the JSON response from H&M API and formats product data.
    """
    items = []
    product_list = json_data.get("plpList", {}).get("productList", [])

    for product in product_list:
        item = {
            "unique_id": f"{product['id']}-{size}",
            "id": product["id"],
            "name": product["productName"],
            "price": product["prices"][0]["price"],
            "size": size,
            "category": category_name,
            "url": f"https://www2.hm.com{product['url']}",
            "image_url": product["swatches"][0]["productImage"] if product["swatches"] else None,
            "availability": product["availability"]["stockState"],
        }
        items.append(item)

    return items


def fetch_all_pages_with_size(category_name, sizes=None, connection=None):
    """
    Fetches all products for a given category and size filters, handling pagination.
    Stores results in the database if a connection is provided.
    """
    CATEGORY_ID_MAP = {
        "View All": "men_viewall",
        "Hoodies and Sweatshirts": "men_hoodiessweatshirts",
        "Jeans":  "men_jeans",
        "Jumpers": "men_cardigansjumpers",
    }
    SIZE_CODE_MAP = {
        "2XL": "menswear;NO_FORMAT[SML];XXL",
        "3XL": "menswear;NO_FORMAT[SML];3XL",
        "W38 L34": "waist;NO_FORMAT[Numeric/Numeric];38/34",
        "W38 L38": "waist;NO_FORMAT[Numeric/Numeric];38/38",

    }

    category_id = CATEGORY_ID_MAP.get(category_name)
    if not category_id:
        print(f"Invalid category name: {category_name}")
        return []

    size_codes = [SIZE_CODE_MAP[size] for size in sizes if size in SIZE_CODE_MAP]

    all_items = []
    for size, size_code in zip(sizes, size_codes):
        page = 1
        while True:
            print(f"Fetching data for category '{category_name}', size '{size}', page {page}...")
            data = fetch_hnm_data(category_id, size_filter=size_code, page=page)

            # Stop if no more products found
            if not data or not data.get("plpList", {}).get("productList", []):
                print(f"No more products found for size '{size}'. Stopping pagination.")
                break

            items = parse_hnm_data(data, size, category_name)
            all_items.extend(items)

            # Store fetched items in the database
            if connection:
                store_in_db(items, connection)

            print(f"Stored {len(items)} items for size '{size}', page {page}.")
            page = data.get("pagination", {}).get("nextPageNum")
            if not page:
                break

    return all_items

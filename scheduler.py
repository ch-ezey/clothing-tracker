import schedule
import time
from datetime import datetime
from scrapers.asos_scraper import fetch_all_pages_with_size as fetch_asos
from scrapers.hnm_scraper import fetch_all_pages_with_size as fetch_hnm
from db.database import setup_database


def fetch_data(connection, asos_categories_and_sizes, hnm_categories_and_sizes, test_mode=False):
    """
    Fetch data from both ASOS and H&M, store in the database, and remove stale items.
    """
    print(f"[{datetime.now()}] Starting data fetch...")

    # Track active items
    active_items = set()

    # ASOS
    for entry in asos_categories_and_sizes:
        category_name = entry["category_name"]
        sizes = entry["sizes"]
        fetched_items = fetch_asos(category_name, sizes=sizes, connection=connection)

        if test_mode:
            print(f"Fetched {len(fetched_items)} items from ASOS for {category_name} with sizes {sizes}:")
            # Print only the first 3 items
            for i, item in enumerate(fetched_items[:3]):
                print(f"Item {i+1}: {item}")

        active_items.update(item["unique_id"] for item in fetched_items)

    # H&M
    for entry in hnm_categories_and_sizes:
        category_name = entry["category_name"]
        sizes = entry["sizes"]
        fetched_items = fetch_hnm(category_name, sizes=sizes, connection=connection)

        if test_mode:
            print(f"Fetched {len(fetched_items)} items from H&M for {category_name} with sizes {sizes}:")
            # Print only the first 3 items
            for i, item in enumerate(fetched_items[:3]):
                print(f"Item {i+1}: {item}")

        active_items.update(item["unique_id"] for item in fetched_items)

    # Remove stale items from the database
    remove_stale_items(connection, active_items)

    print(f"[{datetime.now()}] Data fetch completed.")


def remove_stale_items(connection, active_items):
    """
    Remove items from the database that are no longer found on the websites.
    """
    cursor = connection.cursor()
    # Fetch all stored unique_ids from the database
    cursor.execute("SELECT unique_id FROM items")
    stored_items = {row[0] for row in cursor.fetchall()}

    # Determine stale items (in database but not in active_items)
    stale_items = stored_items - active_items
    if stale_items:
        print(f"Removing {len(stale_items)} stale items from the database...")
        cursor.executemany("DELETE FROM items WHERE unique_id = ?", [(item,) for item in stale_items])
        connection.commit()
        print(f"Removed {len(stale_items)} stale items.")
    else:
        print("No stale items found to remove.")


def schedule_updates(asos_categories_and_sizes, hnm_categories_and_sizes, connection, test_mode=False):
    print("Scheduling updates...")

    # Use fetch_data with test_mode flag
    fetch_data(connection, asos_categories_and_sizes, hnm_categories_and_sizes, test_mode=test_mode)

    print("Updates completed.")


def manual_update(asos_categories_and_sizes, hnm_categories_and_sizes, connection, test_mode=False):
    """
    Manually updates the database with new product data for ASOS and H&M.
    """
    print("Performing manual update...")

    # Perform the same update process for ASOS
    for category_and_size in asos_categories_and_sizes:
        category_name = category_and_size["category_name"]
        sizes = category_and_size["sizes"]
        print(f"Fetching data for {category_name} with sizes {sizes}...")
        fetched_items = fetch_asos(category_name, sizes=sizes, connection=connection)

        if test_mode:
            print(f"Fetched {len(fetched_items)} items from ASOS for {category_name} with sizes {sizes}:")
            # Print only the first 3 items
            for i, item in enumerate(fetched_items[:3]):
                print(f"Item {i+1}: {item}")

    # Perform the same update process for H&M
    for category_and_size in hnm_categories_and_sizes:
        category_name = category_and_size["category_name"]
        sizes = category_and_size["sizes"]
        print(f"Fetching data for {category_name} with sizes {sizes}...")
        fetched_items = fetch_hnm(category_name, sizes=sizes, connection=connection)

        if test_mode:
            print(f"Fetched {len(fetched_items)} items from H&M for {category_name} with sizes {sizes}:")
            # Print only the first 3 items
            for i, item in enumerate(fetched_items[:3]):
                print(f"Item {i+1}: {item}")

    print("Manual update completed.")


# Set up the scheduler for periodic updates (e.g., daily, weekly, etc.)
def setup_scheduler(asos_categories_and_sizes, hnm_categories_and_sizes, connection, test_mode=False):
    """
    Schedules automatic updates at specified intervals.
    """
    schedule.every().day.at("00:00").do(schedule_updates, asos_categories_and_sizes=asos_categories_and_sizes,
                                          hnm_categories_and_sizes=hnm_categories_and_sizes, connection=connection, test_mode=test_mode)

    while True:
        schedule.run_pending()
        time.sleep(60)  # Wait for the next scheduled time

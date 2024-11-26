import argparse
from scheduler import schedule_updates, manual_update
from db.database import setup_database

def main():
    # Assign categories and sizes
    asos_categories_and_sizes = [
        {"category_name": "Jumpers", "sizes": ["3XL"]},
        # {"category_name": "Shoes", "sizes": ["Size 14"]},
    ]
    hnm_categories_and_sizes = [
        # {"category_name": "Hoodies and Sweatshirts", "sizes": ["XXL"]},
    ]

    # Command-line argument parsing
    parser = argparse.ArgumentParser(description="Clothing Database Updater")
    parser.add_argument(
        "--schedule", action="store_true", help="Run the scheduler for automatic updates."
    )
    parser.add_argument(
        "--manual", action="store_true", help="Trigger a manual update."
    )
    parser.add_argument(
        "--test_mode", action="store_true", help="Use test mode (in-memory database)."
    )
    args = parser.parse_args()

    # Determine if test_mode is enabled
    test_mode = args.test_mode

    # Set up the database connection (in-memory or persistent)
    print("Setting up database...")
    connection = setup_database(test_mode)

    try:
        if args.schedule:
            print("Running scheduler for automatic updates...")
            schedule_updates(asos_categories_and_sizes, hnm_categories_and_sizes, connection, test_mode=test_mode)
        elif args.manual:
            print("Running manual update...")
            manual_update(asos_categories_and_sizes, hnm_categories_and_sizes, connection, test_mode=test_mode)
        else:
            print("Please specify --schedule or --manual. Use -h for help.")
    finally:
        # Close the connection when done
        connection.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main()

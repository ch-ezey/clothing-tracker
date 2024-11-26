# Clothing Tracker

A Python-based platform for tracking clothing sizes and availability across multiple retailer websites, including ASOS and H&M.

## Features

- Automatically fetches and updates clothing data for specified categories and sizes.
- Supports manual and scheduled updates.
- Removes outdated items from the database.
- Uses SQLite for efficient local data storage.

## Setup Instructions

### 1. Clone the repository:

```bash
git clone https://github.com/ch-ezey/clothing-tracker.git
cd clothing-tracker
```

### 2. Set up a virtual environment

```bash
python -m venv env
source env/bin/activate    # On Windows: env\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the program:

```bash
python main.py --manual
```

## Usage

### Automatic Updates

- Run the script with the --schedule flag to enable automatic updates:

```bash
python main.py --schedule
```

### Manual Updates

- Fetch product data manually with the --manual flag:

```bash
python main.py --manual
```

### Test Mode

- Use the --test_mode flag for an in-memory SQLite database (for development and testing):

```bash
python main.py --manual --test_mode
```

## Project Structure

clothing_tracker/
├── scrapers/                # Modules for fetching data from websites
│   ├── asos_scraper.py      # ASOS-specific scraping logic
│   ├── hnm_scraper.py       # H&M-specific scraping logic
│
├── db/                      # Database management and utilities
│   ├── database.py          # SQLite database setup and management
│
├── scheduler/               # Modules for scheduling updates
│   ├── scheduler.py         # Handles manual and scheduled updates
│
├── main.py                  # Entry point for the application
├── requirements.txt         # Project dependencies
├── .gitignore               # Files to ignore in Git
└── README.md                # Project documentation

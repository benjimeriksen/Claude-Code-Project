"""Run all collectors and save results to the database.

Usage:  python collect.py            # live data from the real APIs
        python collect.py --sample   # offline sample data (no network/keys)
"""
import argparse

from dotenv import load_dotenv

import db
from collectors import github

load_dotenv()  # reads GITHUB_TOKEN etc. from the .env file


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", action="store_true", help="use offline sample data")
    args = parser.parse_args()

    conn = db.connect()
    print("Collecting from GitHub" + (" (sample data)..." if args.sample else "..."))
    items = github.load_sample() if args.sample else github.collect()
    count = db.save_items(conn, items)
    print(f"  saved {count} repos")
    total = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
    print(f"Database now holds {total} items.")


if __name__ == "__main__":
    main()

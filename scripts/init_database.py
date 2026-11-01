"""
Script: init_database.py
Initializes the SQLite schema, creates indexes, and provisions default administrator account.
"""

import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv()

from src.database import BatteryDatabase
from src.auth import AuthManager


def main():
    print("=" * 60)
    print("Initializing Battery Monitoring SQLite Database...")
    print("=" * 60)

    db_path = os.getenv("DATABASE_PATH", "data/battery.db")
    db = BatteryDatabase(db_path=db_path)
    print(f"[OK] Database initialized at: {os.path.abspath(db_path)}")

    auth = AuthManager(db)
    print(f"[OK] Default administrator verified in database.")
    print("Initialization completed successfully.\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Initialize the clients database if it does not exist.
Maintained by Htet Shine Aung (2604711)
"""

import sys
from pathlib import Path

# Resolve project root and ensure it is in Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DB_PATH = PROJECT_ROOT / "clients.db"

from io_manager import IOManager
from data_manager import UserManager


def init_database() -> None:
    """Create and seed the database if necessary."""
    db_existed = DB_PATH.exists()
    
    # Initialize UserManager (creates schema/file if missing)
    _ = UserManager(str(DB_PATH))

    if db_existed:
        IOManager.print_update(f"Database already exists at {DB_PATH.name}. Schema verified.")
    else:
        IOManager.print_update(f"Database initialized successfully at {DB_PATH.name}!")


if __name__ == "__main__":
    init_database()
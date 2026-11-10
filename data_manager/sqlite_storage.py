import json
import sqlite3
from pathlib import Path
from typing import Any

from .storage import Storage


class SQLiteStorage(Storage):
    def __init__(self, database_path: str = "clients.db") -> None:
        self._database_path = str(database_path)

        # Create the database and table if necessary
        self._initialize_database()
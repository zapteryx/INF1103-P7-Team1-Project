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

    def _connect(self) -> sqlite3.Connection:
        """
        Create a connection to the SQLite database.
        """
        connection = sqlite3.connect(
            self._database_path,
            timeout=10
        )

        connection.row_factory = sqlite3.Row
        return connection
    
    def _initialize_database(self) -> None:
        if self._database_path != ":memory:":
            Path(self._database_path).parent.mkdir(
                parents=True,
                exist_ok=True
            )

        with self._connect() as connection:
                connection.execute("""
                    CREATE TABLE IF NOT EXISTS clients (
                        client_id TEXT PRIMARY KEY,
                        gender TEXT,
                        age INTEGER,
                        dependents INTEGER,
                        care_type TEXT,
                        special_needs TEXT,
                        intake_notes TEXT,
                        outcome INTEGER CHECK (
                            outcome IN (0, 1)
                            OR outcome IS NULL
                        ),
                        accepted_shelter TEXT,
                        extra_fields TEXT NOT NULL DEFAULT '{}'
                    )
                """)

    @staticmethod
    def _encode(record: dict[str, Any]) -> tuple:
        client_id = str(
            record.get("client_id", "")
        ).strip()

        if not client_id:
            raise ValueError("Client ID cannot be empty.")

        outcome = record.get("outcome")

        if outcome is not None and type(outcome) is not bool:
            raise ValueError(
                "Outcome must be True, False, or None."
            )

        known_fields = {
            "client_id",
            "gender",
            "age",
            "dependents",
            "care_type",
            "special_needs",
            "intake_notes",
            "outcome",
            "accepted_shelter"
        }

        extra_fields = {
            key: value
            for key, value in record.items()
            if key not in known_fields
        }

        accepted_shelter = (
            json.dumps(record["accepted_shelter"])
            if "accepted_shelter" in record
            else None
        )

        return (
            client_id,
            record.get("gender"),
            record.get("age"),
            record.get("dependents"),
            record.get("care_type"),
            record.get("special_needs"),
            record.get("intake_notes"),
            None if outcome is None else int(outcome),
            accepted_shelter,
            json.dumps(extra_fields)
        )
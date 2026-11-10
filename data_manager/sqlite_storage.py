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
    
    @staticmethod
    def _decode(row: sqlite3.Row) -> dict[str, Any]:
        record = {
            "client_id": row["client_id"]
        }

        fields = (
            "gender",
            "age",
            "dependents",
            "care_type",
            "special_needs",
            "intake_notes"
        )

        for field in fields:
            if row[field] is not None:
                record[field] = row[field]

        outcome = row["outcome"]

        record["outcome"] = (
            None if outcome is None else bool(outcome)
        )

        if row["accepted_shelter"] is not None:
            record["accepted_shelter"] = json.loads(
                row["accepted_shelter"]
            )

        record.update(json.loads(row["extra_fields"]))

        return record

    def load_records(
        self
    ) -> tuple[list[dict[str, Any]], str | None]:
        try:
            with self._connect() as connection:
                rows = connection.execute(
                    "SELECT * FROM clients ORDER BY rowid"
                ).fetchall()

            records = [
                self._decode(row)
                for row in rows
            ]

            return records, None

        except (sqlite3.Error, ValueError, TypeError) as error:
            return [], f"SQLite load failed: {error}"

    def save_records(
        self,
        records: list[dict[str, Any]]
    ) -> tuple[bool, str | None]:
        if not isinstance(records, list):
            return False, "Records must be a list."

        if not all(isinstance(r, dict) for r in records):
            return False, "Every record must be a dictionary."

        try:
            values = [
                self._encode(record)
                for record in records
            ]

            with self._connect() as connection:
                connection.execute(
                    "DELETE FROM clients"
                )

                connection.executemany("""
                    INSERT INTO clients (
                        client_id,
                        gender,
                        age,
                        dependents,
                        care_type,
                        special_needs,
                        intake_notes,
                        outcome,
                        accepted_shelter,
                        extra_fields
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, values)

            return True, None

        except (
            sqlite3.Error,
            ValueError,
            TypeError,
            OverflowError
        ) as error:
            return False, f"SQLite save failed: {error}"
        
    def insert_record(
        self,
        record: dict[str, Any]
    ) -> tuple[bool, str | None]:
        try:
            values = self._encode(record)

            with self._connect() as connection:
                connection.execute("""
                    INSERT INTO clients (
                        client_id,
                        gender,
                        age,
                        dependents,
                        care_type,
                        special_needs,
                        intake_notes,
                        outcome,
                        accepted_shelter,
                        extra_fields
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, values)

            return True, None

        except (
            sqlite3.Error,
            ValueError,
            TypeError,
            OverflowError
        ) as error:
            return False, f"SQLite insert failed: {error}"

    def get_record(
        self,
        client_id: str
    ) -> tuple[dict[str, Any] | None, str | None]:
        try:
            with self._connect() as connection:
                row = connection.execute(
                    """
                    SELECT * FROM clients
                    WHERE client_id = ?
                    """,
                    (str(client_id),)
                ).fetchone()

            if row is None:
                return None, "Client record not found."

            return self._decode(row), None

        except (sqlite3.Error, ValueError, TypeError) as error:
            return None, f"SQLite lookup failed: {error}"

    def update_record(
        self,
        client_id: str,
        **changes: Any
    ) -> tuple[bool, str | None]:
        if not changes:
            return False, "No fields provided for update."

        if "client_id" in changes:
            return False, "Client ID cannot be changed."

        record, error = self.get_record(client_id)

        if error:
            return False, error

        record.update(changes)

        try:
            values = self._encode(record)

            with self._connect() as connection:
                connection.execute("""
                    UPDATE clients
                    SET gender = ?,
                        age = ?,
                        dependents = ?,
                        care_type = ?,
                        special_needs = ?,
                        intake_notes = ?,
                        outcome = ?,
                        accepted_shelter = ?,
                        extra_fields = ?
                    WHERE client_id = ?
                """, values[1:] + (values[0],))

            return True, None

        except (
            sqlite3.Error,
            ValueError,
            TypeError,
            OverflowError
        ) as error:
            return False, f"SQLite update failed: {error}"

    def delete_record(
        self,
        client_id: str
    ) -> tuple[bool, str | None]:
        try:
            with self._connect() as connection:
                cursor = connection.execute(
                    """
                    DELETE FROM clients
                    WHERE client_id = ?
                    """,
                    (str(client_id),)
                )

                deleted = cursor.rowcount

            if deleted == 0:
                return False, "Client record not found."

            return True, None

        except sqlite3.Error as error:
            return False, f"SQLite delete failed: {error}"
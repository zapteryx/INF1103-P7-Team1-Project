
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from contextlib import closing


# Maintained by Htet Shine Aung (2604711)
@dataclass(frozen=True)
class User:
    user_id: int
    name: str
    username: str
    nric: str
    is_admin: bool
    password_hash: str
    registration_date: str
    account_status: int

    @property
    def is_active(self) -> bool:
        return self.account_status == 1


# Maintained by Htet Shine Aung (2604711)
class UserManager:

    def __init__(self, database_path: str = "clients.db"):
        self._database_path = str(database_path)

        Path(self._database_path).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self._initialize_database()

    # Maintained by Htet Shine Aung (2604711)
    def _connect(self):
        connection = sqlite3.connect(
            self._database_path,
            timeout=10
        )
        connection.row_factory = sqlite3.Row
        return connection

    # Maintained by Htet Shine Aung (2604711)
    def _initialize_database(self):
        with closing(self._connect()) as connection:
            with connection:

                # Create the users table
                connection.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        username TEXT NOT NULL UNIQUE,
                        nric TEXT UNIQUE,
                        is_admin INTEGER NOT NULL DEFAULT 0 CHECK (is_admin IN (0, 1)),
                        password_hash TEXT NOT NULL,
                        registration_date TEXT NOT NULL,
                        account_status INTEGER NOT NULL DEFAULT 1
                            CHECK (account_status IN (0, 1))
                    )
                """)

                # Make the first generated user ID 1001
                connection.execute("""
                    INSERT OR IGNORE INTO sqlite_sequence
                        (name, seq)
                    VALUES ('users', 1000)
                """)

                # Do not reset existing user IDs
                connection.execute("""
                    UPDATE sqlite_sequence
                    SET seq = 1000
                    WHERE name = 'users'
                      AND seq < 1000
                """)

    # Maintained by Htet Shine Aung (2604711)
    # Return a User object if found, otherwise None.
    def get_user_by_username(
        self,
        username: str
    ) -> User | None:

        if not isinstance(username, str):
            return None

        username = username.strip()

        if not username:
            return None

        with closing(self._connect()) as connection:
            row = connection.execute("""
                SELECT
                    user_id,
                    name,
                    username,
                    nric,
                    is_admin,
                    password_hash,
                    registration_date,
                    account_status
                FROM users
                WHERE username = ?
            """, (username,)).fetchone()

        if row is None:
            return None

        return User(
            user_id=row["user_id"],
            name=row["name"],
            username=row["username"],
            nric=row["nric"],
            is_admin=row["is_admin"],
            password_hash=row["password_hash"],
            registration_date=row["registration_date"],
            account_status=row["account_status"]
        )

    # Maintained by Htet Shine Aung (2604711)
    # Register a new user.
    # Returns user_id on success, None on failure.
    def create_user(
        self,
        name: str,
        nric: str,
        username: str,
        password_hash: str,
        is_admin: bool = False,
    ) -> int | None:

        if not all(
            isinstance(value, str)
            for value in (name, username, password_hash)
        ):
            return None
        
        nric = nric.strip()
        name = name.strip()
        username = username.strip()
        
        if nric == "0":     #admin nric is 0, will now be None for admin registration
            nric = None

        if not name or not username or not password_hash:
            return None

        registration_date = datetime.now().isoformat(
            timespec="seconds"
        )

        try:
            with closing(self._connect()) as connection:
                with connection:
                    cursor = connection.execute("""
                        INSERT INTO users (
                            name,
                            username,
                            nric,
                            password_hash,
                            is_admin,
                            registration_date,
                            account_status
                        )
                        VALUES (?, ?, ?, ?, ?, ?, 1)
                    """, (
                        name,
                        username,
                        nric,
                        password_hash,
                        is_admin,
                        registration_date
                    ))

                    user_id = cursor.lastrowid

            return user_id

        except sqlite3.Error:
            return None

    # Maintained by Htet Shine Aung (2604711)
    # Set account_status to 1 (active) or 0 (inactive).
    def update_account_status(
        self,
        user_id: int,
        account_status: int
    ) -> bool:

        if (
            type(user_id) is not int
            or type(account_status) is not int
            or account_status not in (0, 1)
        ):
            return False

        try:
            with closing(self._connect()) as connection:
                with connection:
                    cursor = connection.execute("""
                        UPDATE users
                        SET account_status = ?
                        WHERE user_id = ?
                    """, (
                        account_status,
                        user_id
                    ))

                    updated = cursor.rowcount > 0

            return updated

        except sqlite3.Error:
            return False

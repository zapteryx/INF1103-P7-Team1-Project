import csv
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

# Resolve project root and append to sys.path so 'main', 'ai_manager', etc. import cleanly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import main
from data_manager import SQLiteStorage, UserManager, Authentication

# Maintained by Max (2604426)

# Test files resolved relative to project root
TEST_CLIENTS_JSON = str(PROJECT_ROOT / "clients-test.json")
TEST_CLIENTS_CSV = str(PROJECT_ROOT / "clients-test.csv")
TEST_CLIENTS_DB = str(PROJECT_ROOT / "clients-test.db")
SHELTER_DIR_CSV = str(PROJECT_ROOT / "singapore_shelters_directory.csv")

# Fake AI output that simulates a valid Gemini API response
FAKE_AI_RESPONSE = {
    "urgency_level": 3,
    "criteria_met": [
        {
            "shelter_name": "Transit Point @ Margaret Drive (New Hope Community Services)",
            "criteria": "Met age and gender criteria",
            "gender_restriction": "Any",
            "dependents_allowed": True,
            "min_age": 18,
            "max_age": 60,
            "ai_confidence_score": 0.95,
            "suitability_score": 85.0,
        }
    ],
}


def setup_test_environment():
    """Clear/initialize JSON, CSV, and SQLite test files before running tests."""
    # Initialize JSON test file
    with open(TEST_CLIENTS_JSON, "w", encoding="utf-8") as f:
        json.dump([], f, indent=4)
    print(f"PASS: Test environment initialized: {TEST_CLIENTS_JSON} cleared")

    # Initialize CSV test file with headers only
    with open(TEST_CLIENTS_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "client_id",
                "gender",
                "age",
                "dependents",
                "care_type",
                "special_needs",
                "intake_notes",
                "outcome",
            ],
        )
        writer.writeheader()
    print(f"PASS: Test environment initialized: {TEST_CLIENTS_CSV} cleared")

    # Clean up stale DB and re-initialize SQLite test database schema
    if os.path.exists(TEST_CLIENTS_DB):
        try:
            os.remove(TEST_CLIENTS_DB)
        except OSError:
            pass

    db_storage = SQLiteStorage(TEST_CLIENTS_DB)
    if hasattr(db_storage, "close") and callable(getattr(db_storage, "close")):
        db_storage.close()

    print(f"PASS: Test environment initialized: {TEST_CLIENTS_DB} cleared & schema created")

    # Setup test user for authentication
    user_manager = UserManager(TEST_CLIENTS_DB)
    auth = Authentication(user_manager)

    # Register a test user if not exists
    if auth.is_username_available("testuser"):
        auth.register_user(name="Test User", nric="S1111112A", username="testuser", password="TestPass123!")
        print("PASS: Test user created for authentication\n")
    else:
        print("PASS: Test user already exists\n")


def test_menu_options():
    # Setup clean test environment across all formats
    setup_test_environment()
    print("==================================================")
    print("STARTING MENU OPTIONS TEST (JSON, CSV, & SQLITE)")
    print("==================================================\n")

    # Mock authentication to bypass login for testing
    # First call returns user, second call returns None (simulating exit after logout)
    call_count = {"count": 0}

    def mock_authenticate():
        call_count["count"] += 1
        if call_count["count"] == 1:
            from data_manager import UserManager, Authentication
            user_manager = UserManager(TEST_CLIENTS_DB)
            auth = Authentication(user_manager)
            auth.login("testuser", "TestPass123!")
            return auth.get_current_user()
        else:
            return None  # Simulate user choosing to exit on subsequent calls

    # Mock ai_manager.get_shelter_recommendation so no external API calls are made
    with patch(
        "ai_manager.AIManager.get_shelter_recommendation",
        return_value=FAKE_AI_RESPONSE,
    ), patch(
        "main.authenticate_user",
        side_effect=mock_authenticate
    ):

        # --- OPTION 1: NEW CLIENT INTAKE ---
        print("--- Testing Option 1: New Client Intake (JSON) ---")
        inputs_option_1 = [
            "1",  # Select Option 1 (New Client Intake)
            "S1234567A",  # NRIC
            "Male",  # Gender
            "30",  # Age
            "1",  # Dependents
            "Short Term",  # Care Type
            "No",  # Special Needs
            "Test intake note",  # Intake notes
            TEST_CLIENTS_JSON,  # Client file path
            "6",  # Select Option 6 (Exit)
        ]
        with patch("builtins.input", side_effect=inputs_option_1):
            main.main()
        print("PASS: Option 1 (JSON) executed successfully.\n")

        print("--- Testing Option 1b: New Client Intake (CSV) ---")
        inputs_option_1b = [
            "1",
            "S9999999B",
            "Female",
            "25",
            "0",
            "Long Term",
            "Yes",
            "CSV test client",
            TEST_CLIENTS_CSV,
            "6",
        ]
        with patch("builtins.input", side_effect=inputs_option_1b):
            main.main()
        print("PASS: Option 1b (CSV) executed successfully.\n")

        print("--- Testing Option 1c: New Client Intake (SQLite DB) ---")
        inputs_option_1c = [
            "1",
            "S8888888C",
            "Male",
            "40",
            "2",
            "Short Term",
            "No",
            "SQLite test client",
            TEST_CLIENTS_DB,
            "6",
        ]
        with patch("builtins.input", side_effect=inputs_option_1c):
            main.main()
        print("PASS: Option 1c (SQLite DB) executed successfully.\n")

        # --- OPTION 2: VIEW ALL SHELTERS ---
        print("--- Testing Option 2: View All Shelters ---")
        inputs_option_2 = [
            "2",  # Select Option 2 (View All Shelters)
            SHELTER_DIR_CSV,  # Shelter CSV filename
            "6",  # Select Option 6 (Exit)
        ]
        with patch("builtins.input", side_effect=inputs_option_2):
            main.main()
        print("PASS: Option 2 executed successfully.\n")

        # --- OPTION 3: SHELTER RECOMMENDATIONS ---
        print("--- Testing Option 3: Get Shelter Recommendations (JSON) ---")

        def option_3_inputs():
            yield "3"
            yield SHELTER_DIR_CSV
            yield TEST_CLIENTS_JSON
            while True:
                yield "yes"

        with patch(
            "builtins.input", side_effect=option_3_inputs()
        ), patch.object(main.IOManager, "print_error") as mock_print_error:
            menu_calls = 0

            def mock_display_menu():
                nonlocal menu_calls
                menu_calls += 1
                if menu_calls > 1:
                    return 6
                return 3

            with patch.object(
                main.IOManager, "display_menu", side_effect=mock_display_menu
            ):
                main.main()

            assert not mock_print_error.called, (
                f"Option 3 (JSON) failed with error(s): {mock_print_error.call_args_list}"
            )

        print("PASS: Option 3 (JSON) executed successfully.\n")

        print("--- Testing Option 3b: Get Shelter Recommendations (CSV) ---")

        def option_3b_inputs():
            yield "3"
            yield SHELTER_DIR_CSV
            yield TEST_CLIENTS_CSV
            while True:
                yield "yes"

        with patch(
            "builtins.input", side_effect=option_3b_inputs()
        ), patch.object(main.IOManager, "print_error") as mock_print_error_csv:
            menu_calls_csv = 0

            def mock_display_menu_csv():
                nonlocal menu_calls_csv
                menu_calls_csv += 1
                if menu_calls_csv > 1:
                    return 6
                return 3

            with patch.object(
                main.IOManager, "display_menu", side_effect=mock_display_menu_csv
            ):
                main.main()

            assert not mock_print_error_csv.called, (
                f"Option 3b (CSV) failed with error(s): {mock_print_error_csv.call_args_list}"
            )

        print("PASS: Option 3b (CSV) executed successfully.\n")

        print("--- Testing Option 3c: Get Shelter Recommendations (SQLite DB) ---")

        def option_3c_inputs():
            yield "3"
            yield SHELTER_DIR_CSV
            yield TEST_CLIENTS_DB
            while True:
                yield "yes"

        with patch(
            "builtins.input", side_effect=option_3c_inputs()
        ), patch.object(main.IOManager, "print_error") as mock_print_error_db:
            menu_calls_db = 0

            def mock_display_menu_db():
                nonlocal menu_calls_db
                menu_calls_db += 1
                if menu_calls_db > 1:
                    return 6
                return 3

            with patch.object(
                main.IOManager, "display_menu", side_effect=mock_display_menu_db
            ):
                main.main()

            assert not mock_print_error_db.called, (
                f"Option 3c (SQLite DB) failed with error(s): {mock_print_error_db.call_args_list}"
            )

        print("PASS: Option 3c (SQLite DB) executed successfully.\n")

        # --- OPTION 4: SEARCH CLIENT BY NRIC ---
        print("--- Testing Option 4: Search Client by NRIC (JSON) ---")
        inputs_option_4 = ["4", TEST_CLIENTS_JSON, "S1234567A", "6"]
        with patch("builtins.input", side_effect=inputs_option_4):
            main.main()
        print("PASS: Option 4 (JSON) executed successfully.\n")

        print("--- Testing Option 4b: Search Client by NRIC (CSV) ---")
        inputs_option_4b = ["4", TEST_CLIENTS_CSV, "S9999999B", "6"]
        with patch("builtins.input", side_effect=inputs_option_4b):
            main.main()
        print("PASS: Option 4b (CSV) executed successfully.\n")

        print("--- Testing Option 4c: Search Client by NRIC (SQLite DB) ---")
        inputs_option_4c = ["4", TEST_CLIENTS_DB, "S8888888C", "6"]
        with patch("builtins.input", side_effect=inputs_option_4c):
            main.main()
        print("PASS: Option 4c (SQLite DB) executed successfully.\n")

        # --- OPTION 5: FILTER CASES BY OUTCOME ---
        print("--- Testing Option 5: Filter Cases by Outcome (JSON) ---")
        inputs_option_5 = ["5", TEST_CLIENTS_JSON, "True", "6"]
        with patch("builtins.input", side_effect=inputs_option_5):
            main.main()
        print("PASS: Option 5 (JSON) executed successfully.\n")

        print("--- Testing Option 5b: Filter Cases by Outcome (CSV) ---")
        inputs_option_5b = ["5", TEST_CLIENTS_CSV, "Accepted", "6"]
        with patch("builtins.input", side_effect=inputs_option_5b):
            main.main()
        print("PASS: Option 5b (CSV) executed successfully.\n")

        print("--- Testing Option 5c: Filter Cases by Outcome (SQLite DB) ---")
        inputs_option_5c = ["5", TEST_CLIENTS_DB, "Accepted", "6"]
        with patch("builtins.input", side_effect=inputs_option_5c):
            main.main()
        print("PASS: Option 5c (SQLite DB) executed successfully.\n")

    print("==================================================")
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("==================================================")


if __name__ == "__main__":
    test_menu_options()
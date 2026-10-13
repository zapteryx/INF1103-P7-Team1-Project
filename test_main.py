import sys
import os
import json
from unittest.mock import patch

import main

# This file is maintained by Ming Xuan (2604426)

# Test files for clients (separate from production data)
TEST_CLIENTS_JSON = "clients-test.json"
TEST_CLIENTS_CSV = "clients-test.csv"

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
            "suitability_score": 85.0
        }
    ]
}


def setup_test_environment():
    """Clear/initialize the test clients files before running tests"""
    # Initialize JSON test file
    with open(TEST_CLIENTS_JSON, 'w', encoding='utf-8') as f:
        json.dump([], f, indent=4)
    print(f"PASS: Test environment initialized: {TEST_CLIENTS_JSON} cleared")

    # Initialize CSV test file with headers only
    import csv
    with open(TEST_CLIENTS_CSV, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['client_id', 'gender', 'age', 'dependents',
                                                'care_type', 'special_needs', 'intake_notes', 'outcome'])
        writer.writeheader()
    print(f"PASS: Test environment initialized: {TEST_CLIENTS_CSV} cleared\n")


def test_menu_options():
    # Setup clean test environment
    setup_test_environment()
    print("==================================================")
    print("STARTING MENU OPTIONS TEST")
    print("==================================================\n")

    # Mock ai_manager.get_shelter_recommendation so no external API calls are made
    with patch("ai_manager.get_shelter_recommendation", return_value=FAKE_AI_RESPONSE):

        # Option 1: Test New Client Intake (JSON)
        print("--- Testing Option 1: New Client Intake (JSON) ---")
        inputs_option_1 = [
            "1",           # Select Option 1 (New Client Intake)
            "S1234567A",   # NRIC
            "Male",        # Gender
            "30",          # Age
            "1",           # Dependents
            "Short Term",  # Care Type
            "No",          # Special Needs
            "Test intake note", # Intake notes
            TEST_CLIENTS_JSON,# Client file path
            "6"            # Select Option 6 (Exit)
        ]
        with patch("builtins.input", side_effect=inputs_option_1):
            main.main()
        print("PASS: Option 1 (JSON) executed successfully.\n")

        # Option 1b: Test New Client Intake (CSV)
        print("--- Testing Option 1b: New Client Intake (CSV) ---")
        inputs_option_1b = [
            "1",           # Select Option 1 (New Client Intake)
            "S9999999B",   # NRIC
            "Female",      # Gender
            "25",          # Age
            "0",           # Dependents
            "Long Term",   # Care Type
            "Yes",         # Special Needs
            "CSV test client", # Intake notes
            TEST_CLIENTS_CSV,# Client file path
            "6"            # Select Option 6 (Exit)
        ]
        with patch("builtins.input", side_effect=inputs_option_1b):
            main.main()
        print("PASS: Option 1b (CSV) executed successfully.\n")

        # Option 2: Test View All Shelters
        print("--- Testing Option 2: View All Shelters ---")
        inputs_option_2 = [
            "2",          # Select Option 2 (View All Shelters)
            "singapore_shelters_directory.csv", # Shelter CSV filename
            "6"            # Select Option 6 (Exit)
        ]
        with patch("builtins.input", side_effect=inputs_option_2):
            main.main()
        print("PASS: Option 2 executed successfully.\n")

        # Option 3: Test Get Shelter Recommendations (JSON)
        print("--- Testing Option 3: Get Shelter Recommendations (JSON) ---")
        # Generator dynamically yields "yes" whenever prompted for a shelter outcome,
        # ensuring all records in clients-test.json are processed regardless of count.
        def option_3_inputs():
            yield "3"                                  # Select Option 3
            yield "singapore_shelters_directory.csv"   # Shelter file path
            yield TEST_CLIENTS_JSON                    # Clients file path
            while True:
                yield "yes"                            # Outcome acceptance for each client

        with patch("builtins.input", side_effect=option_3_inputs()), patch("io_manager.print_error") as mock_print_error:
            # We also mock display_menu after option 3 runs once to break out and exit cleanly
            original_display_menu = main.io_manager.display_menu
            menu_calls = 0

            def mock_display_menu():
                nonlocal menu_calls
                menu_calls += 1
                if menu_calls > 1:
                    return 6  # Select Exit on second iteration
                return 3      # Select Option 3 on first iteration

            with patch("io_manager.display_menu", side_effect=mock_display_menu):
                main.main()

            assert not mock_print_error.called, (
                f"Option 3 (JSON) failed with error(s): {mock_print_error.call_args_list}"
            )

        print("PASS: Option 3 (JSON) executed successfully.\n")

        # Option 3b: Test Get Shelter Recommendations (CSV)
        print("--- Testing Option 3b: Get Shelter Recommendations (CSV) ---")
        def option_3b_inputs():
            yield "3"                                  # Select Option 3
            yield "singapore_shelters_directory.csv"   # Shelter file path
            yield TEST_CLIENTS_CSV                     # Clients file path
            while True:
                yield "yes"                            # Outcome acceptance for each client

        with patch("builtins.input", side_effect=option_3b_inputs()), patch("io_manager.print_error") as mock_print_error_csv:
            menu_calls_csv = 0

            def mock_display_menu_csv():
                nonlocal menu_calls_csv
                menu_calls_csv += 1
                if menu_calls_csv > 1:
                    return 6  # Select Exit on second iteration
                return 3      # Select Option 3 on first iteration

            with patch("io_manager.display_menu", side_effect=mock_display_menu_csv):
                main.main()

            assert not mock_print_error_csv.called, (
                f"Option 3b (CSV) failed with error(s): {mock_print_error_csv.call_args_list}"
            )

        print("PASS: Option 3b (CSV) executed successfully.\n")

        # Option 4: Test Search Client by NRIC (JSON)
        print("--- Testing Option 4: Search Client by NRIC (JSON) ---")
        inputs_option_4 = [
            "4",          # Select Option 4 (Search Client)
            TEST_CLIENTS_JSON,# Client records filename
            "S1234567A",   # Client ID / NRIC
            "6"            # Select Option 6 (Exit)
        ]
        with patch("builtins.input", side_effect=inputs_option_4):
            main.main()
        print("PASS: Option 4 (JSON) executed successfully.\n")

        # Option 4b: Test Search Client by NRIC (CSV)
        print("--- Testing Option 4b: Search Client by NRIC (CSV) ---")
        inputs_option_4b = [
            "4",          # Select Option 4 (Search Client)
            TEST_CLIENTS_CSV,# Client records filename
            "S9999999B",   # Client ID / NRIC
            "6"            # Select Option 6 (Exit)
        ]
        with patch("builtins.input", side_effect=inputs_option_4b):
            main.main()
        print("PASS: Option 4b (CSV) executed successfully.\n")

        # Option 5: Test Filter Cases by Outcome (JSON)
        print("--- Testing Option 5: Filter Cases by Outcome (JSON) ---")
        inputs_option_5 = [
            "5",          # Select Option 5 (Filter Cases by Outcome)
            TEST_CLIENTS_JSON,# Client records filename
            "True",        # Outcome to filter by (True = Accepted)
            "6"            # Select Option 6 (Exit)
        ]
        with patch("builtins.input", side_effect=inputs_option_5):
            main.main()
        print("PASS: Option 5 (JSON) executed successfully.\n")

        # Option 5b: Test Filter Cases by Outcome (CSV)
        print("--- Testing Option 5b: Filter Cases by Outcome (CSV) ---")
        inputs_option_5b = [
            "5",          # Select Option 5 (Filter Cases by Outcome)
            TEST_CLIENTS_CSV,# Client records filename
            "Accepted",    # Outcome to filter by (alternative input format)
            "6"            # Select Option 6 (Exit)
        ]
        with patch("builtins.input", side_effect=inputs_option_5b):
            main.main()
        print("PASS: Option 5b (CSV) executed successfully.\n")

    print("==================================================")
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("==================================================")


if __name__ == "__main__":
    test_menu_options()
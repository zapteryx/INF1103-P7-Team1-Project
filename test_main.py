import sys
import os
from unittest.mock import patch

import main


# Fake AI output that simulates a valid Gemini API response
FAKE_AI_RESPONSE = {
    "urgency_level": 3,
    "criteria_met": [
        {
            "shelter_name": "Hope Haven Shelter",
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


def test_menu_options():
    print("==================================================")
    print("STARTING MENU OPTIONS TEST")
    print("==================================================\n")

    # Mock ai_manager.get_shelter_recommendation so no external API calls are made
    with patch("ai_manager.get_shelter_recommendation", return_value=FAKE_AI_RESPONSE):

        # Option 1: Test New Client Intake
        print("--- Testing Option 1: New Client Intake ---")
        inputs_option_1 = [
            "1",           # Select Option 1 (New Client Intake)
            "S1234567A",   # NRIC
            "Male",        # Gender
            "30",          # Age
            "1",           # Dependents
            "Short Term",  # Care Type
            "No",          # Special Needs
            "Test intake note", # Intake notes
            "clients.json",# Client file path
            "5"            # Select Option 5 (Exit)
        ]
        with patch("builtins.input", side_effect=inputs_option_1):
            main.main()
        print("✓ Option 1 executed successfully.\n")

        # Option 2: Test View All Shelters
        print("--- Testing Option 2: View All Shelters ---")
        inputs_option_2 = [
            "2",          # Select Option 2 (View All Shelters)
            "singapore_shelters_directory.csv", # Shelter CSV filename
            "5"            # Select Option 5 (Exit)
        ]
        with patch("builtins.input", side_effect=inputs_option_2):
            main.main()
        print("✓ Option 2 executed successfully.\n")

        # Option 3: Test Get Shelter Recommendations
        print("--- Testing Option 3: Get Shelter Recommendations ---")
        # Generator dynamically yields "yes" whenever prompted for a shelter outcome,
        # ensuring all records in clients.json are processed regardless of count.
        def option_3_inputs():
            yield "3"                                  # Select Option 3
            yield "singapore_shelters_directory.csv"   # Shelter file path
            yield "clients.json"                       # Clients file path
            while True:
                yield "yes"                            # Outcome acceptance for each client

        with patch("builtins.input", side_effect=option_3_inputs()):
            # We also mock display_menu after option 3 runs once to break out and exit cleanly
            original_display_menu = main.io_manager.display_menu
            menu_calls = 0

            def mock_display_menu():
                nonlocal menu_calls
                menu_calls += 1
                if menu_calls > 1:
                    return 5  # Select Exit on second iteration
                return 3      # Select Option 3 on first iteration

            with patch("io_manager.display_menu", side_effect=mock_display_menu):
                main.main()

        print("✓ Option 3 executed successfully.\n")

        # Option 4: Test Search Client by NRIC
        print("--- Testing Option 4: Search Client by NRIC ---")
        inputs_option_4 = [
            "4",          # Select Option 4 (Search Client)
            "clients.json",# Client records filename
            "S1234567A",   # Client ID / NRIC
            "5"            # Select Option 5 (Exit)
        ]
        with patch("builtins.input", side_effect=inputs_option_4):
            main.main()
        print("✓ Option 4 executed successfully.\n")

    print("==================================================")
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("==================================================")


if __name__ == "__main__":
    test_menu_options()
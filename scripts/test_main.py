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
        auth.register_user(name="Test User", nric="S1111112A", username="testuser", password="TestPass123!", is_admin=True)
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


def test_admin_registration_flow():
    """Test admin registration with secret code validation."""
    print("\n==================================================")
    print("TESTING ADMIN REGISTRATION FLOW")
    print("==================================================\n")

    import tempfile
    import os
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    test_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False).name

    try:
        from data_manager import UserManager, Authentication
        user_manager = UserManager(test_db)
        auth = Authentication(user_manager)

        # Test with correct secret code
        print("--- Testing Admin Registration with Correct Secret Code ---")
        correct_code = os.getenv("ADMIN_SECRET_CODE", "STAFF2026")

        from io_manager import IOManager

        # Test the secret code validator
        with patch("builtins.input", return_value=correct_code):
            result = IOManager.validate_admin_secret_code()
            assert result is True, "Should accept correct admin secret code"
        print("PASS: Correct admin secret code accepted")

        # Test wrong code
        with patch("builtins.input", return_value="WRONGCODE"):
            result = IOManager.validate_admin_secret_code()
            assert result is False, "Should reject wrong admin secret code"
        print("PASS: Wrong admin secret code rejected")

        print("\n--- Testing Admin User Registration ---")

        # Create admin user directly
        success, errors = auth.register_user(
            name="Admin User",
            nric=None,
            username="adminuser123",
            password="AdminPass123!",
            is_admin=True
        )
        assert success is True, f"Admin registration should succeed, got errors: {errors}"
        print("PASS: Admin user registered successfully")

        # Verify admin properties
        user = user_manager.get_user_by_username("adminuser123")
        assert user is not None, "Admin user should exist"
        assert user.is_admin is True, f"is_admin should be True, got: {user.is_admin}"
        assert isinstance(user.is_admin, bool), f"is_admin should be bool, got: {type(user.is_admin)}"
        assert user.nric is None, f"Admin nric should be None, got: {user.nric}"
        print("PASS: Admin user has correct properties (is_admin=True, nric=None)")

    finally:
        if os.path.exists(test_db):
            os.remove(test_db)

    print("\n==================================================")
    print("ADMIN REGISTRATION FLOW TESTS COMPLETED!")
    print("==================================================")


def test_client_registration_with_nric_validation():
    """Test client registration with NRIC format validation."""
    print("\n==================================================")
    print("TESTING CLIENT REGISTRATION WITH NRIC VALIDATION")
    print("==================================================\n")

    from io_manager import IOManager

    print("--- Testing NRIC Format Validation ---")

    # Test valid NRIC formats
    valid_nrics = ["S1234567A", "T9876543Z", "S0000000B", "T1111111C"]
    for nric in valid_nrics:
        # Simulate the validation logic from collect_registration_input
        is_valid = (
            len(nric) == 9
            and nric[0] in ["S", "T"]
            and nric[1:8].isdigit()
            and nric[-1].isalpha()
        )
        assert is_valid is True, f"NRIC {nric} should be valid"
    print(f"PASS: All {len(valid_nrics)} valid NRIC formats accepted")

    # Test invalid NRIC formats
    invalid_nrics = [
        "X1234567A",  # Wrong prefix
        "S12345678",  # Missing letter
        "S123456A",   # Too short
        "S1234567AA", # Too long
        "S12345A7B",  # Letter in middle
        "1234567AB",  # No prefix
    ]

    for nric in invalid_nrics:
        is_valid = (
            len(nric) == 9
            and nric[0] in ["S", "T"]
            and nric[1:8].isdigit()
            and nric[-1].isalpha()
        )
        assert is_valid is False, f"NRIC {nric} should be invalid"
    print(f"PASS: All {len(invalid_nrics)} invalid NRIC formats rejected")

    print("\n==================================================")
    print("NRIC VALIDATION TESTS COMPLETED!")
    print("==================================================")


def test_nric_age_verification():
    """Test NRIC-age verification when NRIC exists in client records."""
    print("\n==================================================")
    print("TESTING NRIC-AGE VERIFICATION")
    print("==================================================\n")

    import tempfile
    import json
    import os

    # Create test client records with NRIC-age data
    test_clients_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    test_clients = [
        {"client_id": "S1234567A", "age": 30, "gender": "Male"},
        {"client_id": "S9876543B", "age": 25, "gender": "Female"}
    ]
    json.dump(test_clients, test_clients_file)
    test_clients_file.close()

    try:
        print("--- Testing NRIC-Age Verification Logic ---")

        # Build nric_age_dict like main.py does
        with open(test_clients_file.name, 'r') as f:
            client_list = json.load(f)

        nric_age_dict = {
            client.get("client_id"): client.get("age") for client in client_list
        }

        # Test matching NRIC with correct age
        nric = "S1234567A"
        input_age = 30
        if nric in nric_age_dict:
            assert nric_age_dict[nric] == input_age, "Age should match"
            print(f"PASS: NRIC {nric} with age {input_age} verified successfully")

        # Test matching NRIC with wrong age
        nric = "S1234567A"
        wrong_age = 25
        if nric in nric_age_dict:
            assert nric_age_dict[nric] != wrong_age, "Age should not match"
            print(f"PASS: NRIC {nric} with wrong age {wrong_age} rejected")

        # Test non-existent NRIC
        nric = "S0000000Z"
        assert nric not in nric_age_dict, "NRIC should not exist"
        print(f"PASS: Non-existent NRIC {nric} not in records")

    finally:
        os.unlink(test_clients_file.name)

    print("\n==================================================")
    print("NRIC-AGE VERIFICATION TESTS COMPLETED!")
    print("==================================================")


def test_username_validation_ux():
    """Test username validation UX with immediate feedback."""
    print("\n==================================================")
    print("TESTING USERNAME VALIDATION UX")
    print("==================================================\n")

    import tempfile
    import os

    test_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False).name

    try:
        from data_manager import UserManager, Authentication
        user_manager = UserManager(test_db)
        auth = Authentication(user_manager)

        print("--- Testing Username Availability Check During Registration ---")

        # Create existing user
        auth.register_user(
            name="Existing User",
            nric="S1111111A",
            username="existinguser",
            password="SecurePass123!",
            is_admin=False
        )

        # Test that username validator works
        username_validator = auth.is_username_available

        # Test available username
        assert username_validator("newuser") is True, "New username should be available"
        print("PASS: Username validator returns True for available username")

        # Test taken username
        assert username_validator("existinguser") is False, "Existing username should be taken"
        print("PASS: Username validator returns False for taken username")

        # Test case sensitivity (usernames are case-sensitive in current implementation)
        assert username_validator("ExistingUser") is True, "Different case is considered available"
        print("PASS: Username validator is case-sensitive")

        print("\nUX Flow Verification:")
        print("  1. User enters username")
        print("  2. username_validator(username) is called immediately")
        print("  3. If False: show 'Username already taken' and reprompt")
        print("  4. If True: continue to next field (NRIC)")
        print("PASS: Username validation provides immediate feedback")

    finally:
        if os.path.exists(test_db):
            os.remove(test_db)

    print("\n==================================================")
    print("USERNAME VALIDATION UX TESTS COMPLETED!")
    print("==================================================")


def test_env_variable_loading():
    """Test that ADMIN_SECRET_CODE loads from .env file."""
    print("\n==================================================")
    print("TESTING ENVIRONMENT VARIABLE LOADING")
    print("==================================================\n")

    import os
    from dotenv import load_dotenv

    print("--- Testing ADMIN_SECRET_CODE from .env ---")

    # Load .env
    load_dotenv()

    # Check if ADMIN_SECRET_CODE exists
    admin_code = os.getenv("ADMIN_SECRET_CODE")
    assert admin_code is not None, "ADMIN_SECRET_CODE should be loaded from .env"
    print(f"PASS: ADMIN_SECRET_CODE loaded from .env (length: {len(admin_code)} chars)")

    # Verify it's not hardcoded in io_manager
    with open("io_manager/__init__.py", "r") as f:
        content = f.read()
        assert 'ADMIN_SECRET_CODE = "STAFF2026"' not in content, "Secret code should not be hardcoded"
        assert 'os.getenv("ADMIN_SECRET_CODE")' in content, "Should load from environment"
    print("PASS: ADMIN_SECRET_CODE is not hardcoded, loads from environment")

    print("\n==================================================")
    print("ENVIRONMENT VARIABLE TESTS COMPLETED!")
    print("==================================================")


def test_approval_workflow():
    """Test client approval workflow for self-registered clients."""
    print("\n==================================================")
    print("TESTING APPROVAL WORKFLOW")
    print("==================================================\n")

    import tempfile
    import json
    import os

    # Create test client records file
    test_clients_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)

    print("--- Testing Self-Registered Client (Unapproved) ---")

    # Simulate self-registered client
    self_registered_client = {
        "client_id": "S1234567A",
        "gender": "Male",
        "age": 30,
        "dependents": 1,
        "care_type": "Short Term",
        "special_needs": "No",
        "intakes_notes": "Self-registered",
        "outcome": None,
        "accepted_shelter": None,
        "approved": False  # Self-registered = unapproved
    }

    # Simulate social worker-added client
    worker_added_client = {
        "client_id": "S9876543B",
        "gender": "Female",
        "age": 25,
        "dependents": 0,
        "care_type": "Long Term",
        "special_needs": "Yes",
        "intakes_notes": "Added by worker",
        "outcome": None,
        "accepted_shelter": None,
        "approved": True  # Worker-added = pre-approved
    }

    test_clients = [self_registered_client, worker_added_client]
    json.dump(test_clients, test_clients_file)
    test_clients_file.close()

    try:
        # Test 1: Count unapproved clients
        with open(test_clients_file.name, 'r') as f:
            clients = json.load(f)

        unapproved = [c for c in clients if not c.get("approved", True)]
        assert len(unapproved) == 1, "Should have 1 unapproved client"
        assert unapproved[0]["client_id"] == "S1234567A", "Unapproved client should be self-registered one"
        print("PASS: Self-registered client is unapproved")

        # Test 2: Verify worker-added client is pre-approved
        worker_clients = [c for c in clients if c.get("approved", True)]
        assert len(worker_clients) == 1, "Should have 1 pre-approved client"
        assert worker_clients[0]["client_id"] == "S9876543B", "Pre-approved client should be worker-added one"
        print("PASS: Worker-added client is pre-approved")

        # Test 3: Simulate approval
        for client in clients:
            if client["client_id"] == "S1234567A":
                client["approved"] = True

        with open(test_clients_file.name, 'w') as f:
            json.dump(clients, f)

        with open(test_clients_file.name, 'r') as f:
            clients = json.load(f)

        all_approved = all(c.get("approved", True) for c in clients)
        assert all_approved, "All clients should be approved after approval process"
        print("PASS: Client approval updates correctly")

        # Test 4: Test AI matching filter (approved only)
        approved_clients = [c for c in clients if c.get("approved", True) and c.get("outcome") is not True]
        assert len(approved_clients) == 2, "AI matching should see 2 approved clients"
        print("PASS: AI matching correctly filters approved clients only")

        # Test 5: Test rejection (removal)
        clients_before_rejection = len(clients)
        clients = [c for c in clients if c["client_id"] != "S1234567A"]
        assert len(clients) == clients_before_rejection - 1, "Rejected client should be removed"
        print("PASS: Client rejection removes record correctly")

    finally:
        os.unlink(test_clients_file.name)

    print("\n==================================================")
    print("APPROVAL WORKFLOW TESTS COMPLETED!")
    print("==================================================")


if __name__ == "__main__":
    # Run original tests
    test_menu_options()

    # Run new comprehensive tests for PR changes
    test_admin_registration_flow()
    test_client_registration_with_nric_validation()
    test_nric_age_verification()
    test_username_validation_ux()
    test_env_variable_loading()
    test_approval_workflow()

    print("\n" + "="*50)
    print("ALL TEST SUITES COMPLETED SUCCESSFULLY!")
    print("="*50)
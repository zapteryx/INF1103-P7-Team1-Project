#!/usr/bin/env python3
"""
Authentication system test suite.
Tests user registration, login, logout, and password validation.
Maintained by Ming Xuan (2604426)
"""

import sys
import os
from pathlib import Path

# Resolve project root and ensure it is in Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data_manager import UserManager, Authentication

# Use temporary file-based database for testing
TEST_DB = str(PROJECT_ROOT / "test_auth.db")


def cleanup_test_db():
    """Remove test database if it exists."""
    if os.path.exists(TEST_DB):
        try:
            os.remove(TEST_DB)
        except OSError:
            pass


def setup_test_auth() -> Authentication:
    """Create a fresh authentication instance with test database."""
    cleanup_test_db()
    user_manager = UserManager(TEST_DB)
    auth = Authentication(user_manager)
    return auth


def test_password_strength_validation():
    """Test password strength requirements."""
    print("--- Testing Password Strength Validation ---")
    auth = setup_test_auth()

    # Test weak password - too short
    errors = auth.check_password_strength("Short1!")
    assert len(errors) > 0, "Should reject short password"
    assert any("12 characters" in error for error in errors)
    print("PASS: Rejected password < 12 characters")

    # Test weak password - missing uppercase
    errors = auth.check_password_strength("lowercase123!")
    assert any("uppercase" in error for error in errors)
    print("PASS: Rejected password without uppercase letter")

    # Test weak password - missing lowercase
    errors = auth.check_password_strength("UPPERCASE123!")
    assert any("lowercase" in error for error in errors)
    print("PASS: Rejected password without lowercase letter")

    # Test weak password - missing digit
    errors = auth.check_password_strength("NoDigitsHere!")
    assert any("digit" in error for error in errors)
    print("PASS: Rejected password without digit")

    # Test weak password - missing symbol
    errors = auth.check_password_strength("NoSymbols123")
    assert any("symbol" in error for error in errors)
    print("PASS: Rejected password without symbol")

    # Test strong password
    errors = auth.check_password_strength("StrongPass123!")
    assert len(errors) == 0, f"Strong password should pass, got errors: {errors}"
    print("PASS: Accepted strong password")

    print()


def test_user_registration():
    """Test user registration flow."""
    print("--- Testing User Registration ---")
    auth = setup_test_auth()

    # Test successful registration
    success, errors = auth.register_user(
        name="John Doe",
        nric="S1234567A",
        username="johndoe123",
        password="SecurePass123!"
    )
    assert success is True, f"Registration should succeed, got errors: {errors}"
    assert errors == [], "Should have no errors on successful registration"
    print("PASS: User registered successfully")

    # Test duplicate username
    success, errors = auth.register_user(
        name="Jane Doe",
        nric="S8901234B",
        username="johndoe123",  # Same username
        password="AnotherPass123!"
    )
    assert success is False, "Should reject duplicate username"
    assert "Username already exists" in errors[0]
    print("PASS: Rejected duplicate username")

    # Test registration with weak password
    success, errors = auth.register_user(
        name="Bob Smith",
        nric="S5678901C",
        username="bobsmith",
        password="weak"
    )
    assert success is False, "Should reject weak password"
    assert len(errors) > 0, "Should return password validation errors"
    print(f"PASS: Rejected weak password with {len(errors)} error(s)")

    print()


def test_user_login():
    """Test user login flow."""
    print("--- Testing User Login ---")
    auth = setup_test_auth()

    # Register a test user first
    auth.register_user(name="Alice Johnson", username="alice123", password="SecurePass123!", nric="S2345678D")

    # Test successful login
    success, message = auth.login("alice123", "SecurePass123!")
    assert success is True, f"Login should succeed, got: {message}"
    assert "Welcome" in message
    print("PASS: User logged in successfully")

    # Verify current user is set
    current_user = auth.get_current_user()
    assert current_user is not None, "Current user should be set after login"
    assert current_user.username == "alice123"
    assert current_user.name == "Alice Johnson"
    print("PASS: Current user is correctly set")

    # Test is_logged_in
    assert auth.is_logged_in() is True
    print("PASS: is_logged_in() returns True")

    # Test wrong password
    auth.logout()  # Reset session
    success, message = auth.login("alice123", "WrongPassword123!")
    assert success is False, "Should reject wrong password"
    assert "Invalid username or password" in message
    assert auth.get_current_user() is None
    print("PASS: Rejected incorrect password")

    # Test non-existent user
    success, message = auth.login("nonexistent", "AnyPass123!")
    assert success is False, "Should reject non-existent user"
    assert "Invalid username or password" in message
    print("PASS: Rejected non-existent user")

    print()


def test_user_logout():
    """Test user logout flow."""
    print("--- Testing User Logout ---")
    auth = setup_test_auth()

    # Register and login
    auth.register_user(name="Bob Wilson", nric="S9012345C", username="bob456", password="SecurePass123!")
    auth.login("bob456", "SecurePass123!")

    assert auth.get_current_user() is not None
    assert auth.is_logged_in() is True
    print("PASS: User is logged in")

    # Logout
    auth.logout()

    assert auth.get_current_user() is None
    assert auth.is_logged_in() is False
    print("PASS: User logged out successfully")

    print()


def test_inactive_account():
    """Test that inactive accounts cannot log in."""
    print("--- Testing Inactive Account Handling ---")

    # Need to use a file-based database to test account status updates
    import os
    test_db_file = str(PROJECT_ROOT / "test_inactive.db")

    try:
        # Remove existing test database
        if os.path.exists(test_db_file):
            os.remove(test_db_file)

        user_manager = UserManager(test_db_file)
        auth = Authentication(user_manager)

        # Register user
        auth.register_user(name="Charlie Brown", nric="S3456789E", username="charlie789", password="SecurePass123!")

        # Login successfully
        success, message = auth.login("charlie789", "SecurePass123!")
        assert success is True
        user = auth.get_current_user()
        user_id = user.user_id
        print("PASS: User logged in with active account")

        # Deactivate account
        auth.logout()
        user_manager.update_account_status(user_id, 0)  # 0 = inactive

        # Try to login with inactive account
        success, message = auth.login("charlie789", "SecurePass123!")
        assert success is False, "Should reject inactive account"
        assert "inactive" in message.lower()
        print("PASS: Rejected login for inactive account")

        # Reactivate account
        user_manager.update_account_status(user_id, 1)  # 1 = active

        # Login should work again
        success, message = auth.login("charlie789", "SecurePass123!")
        assert success is True
        print("PASS: User logged in after account reactivation")

    finally:
        # Cleanup test database
        if os.path.exists(test_db_file):
            os.remove(test_db_file)

    print()


def test_passwords_match():
    """Test password confirmation matching."""
    print("--- Testing Password Matching ---")
    auth = setup_test_auth()

    # Test matching passwords
    assert auth.passwords_match("Password123!", "Password123!") is True
    print("PASS: Correctly identified matching passwords")

    # Test non-matching passwords
    assert auth.passwords_match("Password123!", "Different123!") is False
    print("PASS: Correctly identified non-matching passwords")

    print()


def test_username_availability():
    """Test username availability checking."""
    print("--- Testing Username Availability ---")
    auth = setup_test_auth()

    # Check available username
    assert auth.is_username_available("newuser") is True
    print("PASS: Correctly identified available username")

    # Register user
    auth.register_user(name="Test User", nric="S1111111A", username="newuser", password="SecurePass123!")

    # Check taken username
    assert auth.is_username_available("newuser") is False
    print("PASS: Correctly identified taken username")

    # Check another available username
    assert auth.is_username_available("anotheruser") is True
    print("PASS: Correctly identified different available username")

    print()


def test_admin_user_creation():
    """Test admin user registration with nric=None."""
    print("--- Testing Admin User Creation ---")
    auth = setup_test_auth()

    # Create admin user with nric=None
    success, errors = auth.register_user(
        name="Admin User",
        nric=None,
        username="adminuser",
        password="AdminPass123!",
        is_admin=True
    )
    assert success is True, f"Admin registration should succeed, got errors: {errors}"
    print("PASS: Admin user created with nric=None")

    # Verify admin user can login
    success, message = auth.login("adminuser", "AdminPass123!")
    assert success is True, f"Admin login should succeed, got: {message}"

    user = auth.get_current_user()
    assert user.nric is None, f"Admin NRIC should be None, got: {user.nric}"
    assert user.is_admin is True, f"is_admin should be True, got: {user.is_admin}"
    print("PASS: Admin user has nric=None and is_admin=True")

    print()


def test_client_user_creation_with_nric():
    """Test client user registration with valid NRIC."""
    print("--- Testing Client User Creation with NRIC ---")
    auth = setup_test_auth()

    # Create client user with NRIC
    success, errors = auth.register_user(
        name="Client User",
        nric="S1234567A",
        username="clientuser",
        password="ClientPass123!",
        is_admin=False
    )
    assert success is True, f"Client registration should succeed, got errors: {errors}"
    print("PASS: Client user created with NRIC")

    # Verify client user can login
    success, message = auth.login("clientuser", "ClientPass123!")
    assert success is True, f"Client login should succeed, got: {message}"

    user = auth.get_current_user()
    assert user.nric == "S1234567A", f"Client NRIC should be S1234567A, got: {user.nric}"
    assert user.is_admin is False, f"is_admin should be False, got: {user.is_admin}"
    print("PASS: Client user has correct NRIC and is_admin=False")

    print()


def test_is_admin_bool_type():
    """Test that is_admin is properly converted to bool from SQLite."""
    print("--- Testing is_admin Bool Type Conversion ---")
    auth = setup_test_auth()

    # Create admin user
    auth.register_user(
        name="Bool Test Admin",
        nric=None,
        username="booladmin",
        password="SecurePass123!",
        is_admin=True
    )

    # Create client user
    auth.register_user(
        name="Bool Test Client",
        nric="S9876543B",
        username="boolclient",
        password="SecurePass123!",
        is_admin=False
    )

    # Test admin user
    auth.login("booladmin", "SecurePass123!")
    admin_user = auth.get_current_user()
    assert isinstance(admin_user.is_admin, bool), f"is_admin should be bool, got: {type(admin_user.is_admin)}"
    assert admin_user.is_admin is True, "Admin is_admin should be True"
    assert admin_user.is_admin == True, "Admin is_admin should equal True"
    print("PASS: Admin user is_admin is bool type (True)")

    # Test client user
    auth.logout()
    auth.login("boolclient", "SecurePass123!")
    client_user = auth.get_current_user()
    assert isinstance(client_user.is_admin, bool), f"is_admin should be bool, got: {type(client_user.is_admin)}"
    assert client_user.is_admin is False, "Client is_admin should be False"
    assert client_user.is_admin == False, "Client is_admin should equal False"
    print("PASS: Client user is_admin is bool type (False)")

    # Test Pythonic boolean checks
    auth.logout()
    auth.login("booladmin", "SecurePass123!")
    admin_user = auth.get_current_user()
    if admin_user.is_admin:
        print("PASS: Pythonic 'if user.is_admin:' check works for admin")
    else:
        assert False, "Pythonic boolean check failed for admin"

    auth.logout()
    auth.login("boolclient", "SecurePass123!")
    client_user = auth.get_current_user()
    if not client_user.is_admin:
        print("PASS: Pythonic 'if not user.is_admin:' check works for client")
    else:
        assert False, "Pythonic boolean check failed for client"

    print()


def test_admin_nric_handling():
    """Test that admin users with nric=None don't cause AttributeError."""
    print("--- Testing Admin NRIC None Handling ---")

    import tempfile
    import os

    test_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False).name

    try:
        from data_manager import UserManager, Authentication
        user_manager = UserManager(test_db)
        auth = Authentication(user_manager)

        # Test with nric=None (direct None)
        user_id = user_manager.create_user(
            name="Admin Direct None",
            nric=None,
            username="adminnone",
            password_hash="hash123",
            is_admin=True
        )
        assert user_id is not None, "Should create admin user with nric=None"
        print("PASS: Admin user created with nric=None (direct)")

        # Test with nric="0" (should convert to None)
        user_id2 = user_manager.create_user(
            name="Admin Zero NRIC",
            nric="0",
            username="adminzero",
            password_hash="hash456",
            is_admin=True
        )
        assert user_id2 is not None, "Should create admin user with nric='0'"

        user = user_manager.get_user_by_username("adminzero")
        assert user.nric is None, f"NRIC '0' should convert to None, got: {user.nric}"
        print("PASS: Admin user created with nric='0' converts to None")

    finally:
        if os.path.exists(test_db):
            os.remove(test_db)

    print()


def run_all_tests():
    """Run all authentication tests."""
    print("==================================================")
    print("STARTING AUTHENTICATION SYSTEM TESTS")
    print("==================================================\n")

    try:
        test_password_strength_validation()
        test_passwords_match()
        test_username_availability()
        test_user_registration()
        test_admin_user_creation()
        test_client_user_creation_with_nric()
        test_is_admin_bool_type()
        test_admin_nric_handling()
        test_user_login()
        test_user_logout()
        test_inactive_account()

        print("==================================================")
        print("ALL AUTHENTICATION TESTS COMPLETED SUCCESSFULLY!")
        print("==================================================")
        return True

    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up test database
        cleanup_test_db()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

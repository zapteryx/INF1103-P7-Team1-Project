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
        "John Doe",
        "johndoe123",
        "SecurePass123!"
    )
    assert success is True, f"Registration should succeed, got errors: {errors}"
    assert errors == [], "Should have no errors on successful registration"
    print("PASS: User registered successfully")

    # Test duplicate username
    success, errors = auth.register_user(
        "Jane Doe",
        "johndoe123",  # Same username
        "AnotherPass123!"
    )
    assert success is False, "Should reject duplicate username"
    assert "Username already exists" in errors[0]
    print("PASS: Rejected duplicate username")

    # Test registration with weak password
    success, errors = auth.register_user(
        "Bob Smith",
        "bobsmith",
        "weak"
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
    auth.register_user("Alice Johnson", "alice123", "SecurePass123!")

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
    auth.register_user("Bob Wilson", "bob456", "SecurePass123!")
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
        auth.register_user("Charlie Brown", "charlie789", "SecurePass123!")

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
    auth.register_user("Test User", "newuser", "SecurePass123!")

    # Check taken username
    assert auth.is_username_available("newuser") is False
    print("PASS: Correctly identified taken username")

    # Check another available username
    assert auth.is_username_available("anotheruser") is True
    print("PASS: Correctly identified different available username")

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

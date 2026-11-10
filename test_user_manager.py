
from tempfile import TemporaryDirectory
from pathlib import Path

from data_manager import UserManager


with TemporaryDirectory() as folder:
    db_path = str(Path(folder) / "test_users.db")

    manager = UserManager(db_path)

    print("===== USER DATABASE TEST =====")

    # TEST 1: Register a user
    user_id = manager.create_user(
        "Test User",
        "testuser",
        "test_hash_only"
    )

    print("Registered user ID:", user_id)
    assert user_id == 1001

    # TEST 2: Retrieve user
    user = manager.get_user_by_username("testuser")

    assert user is not None
    assert user.username == "testuser"
    assert user.account_status == 1

    print("Retrieved username:", user.username)
    print("Account status:", user.account_status)

    # TEST 3: Duplicate username
    duplicate = manager.create_user(
        "Another User",
        "testuser",
        "another_test_hash"
    )

    assert duplicate is None
    print("Duplicate username rejected")

    # TEST 4: Deactivate account
    result = manager.update_account_status(
        user_id, 0
    )

    assert result is True
    print("Account deactivated")

    # TEST 5: Verify inactive
    user = manager.get_user_by_username("testuser")

    assert user.account_status == 0
    print("Account status:", user.account_status)

    # TEST 6: Reactivate account
    result = manager.update_account_status(
        user_id, 1
    )

    assert result is True
    print("Account reactivated")

    # TEST 7: Register second user
    second_id = manager.create_user(
        "Second User",
        "seconduser",
        "second_test_hash"
    )

    assert second_id == 1002
    print("Second user ID:", second_id)

    print("===== ALL TESTS PASSED =====")

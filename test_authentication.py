from authentication import Authentication
from user_class import User
from datetime import datetime

class MockDatabase:
    def __init__(self):
        self.users = {}

    def get_user_by_username(self, username):
        return self.users.get(username)

    def create_user(self, name, username, password_hash):
        user_id = len(self.users) + 1001

        registration_date = datetime.now().isoformat()

        user = User(user_id, name, username, password_hash, registration_date)

        self.users[username] = user
        return user_id


database = MockDatabase()
authentication = Authentication(database)

success, errors = authentication.register_user(
    "Sam Denby",
    "samdenby123",
    "Singapore2026!"
)

print(success)
assert errors == []

user = database.get_user_by_username("samdenby123")

print(user.get_user_id())
print(user.get_name())
print(user.get_username())

login_success, message = authentication.login(
    "samdenby123",
    "Singapore2026!"
)

print(login_success)
print(message)


# Test incorrect password
login_success, message = authentication.login(
    "samdenby123",
    "WrongPassword123!"
)

print(login_success)
print(message)

# Test logout
authentication.logout()

current_user = authentication.get_current_user()

print(current_user)

# Test inactive account
user.deactivate_account()

login_success, message = authentication.login(
    "samdenby123",
    "Singapore2026!"
)

print(login_success)
print(message)

# Test same username
success, errors = authentication.register_user(
    "Another Person",
    "samdenby123",
    "AnotherStrong123!"
)

print(success)
assert errors == ["Username already exists."]

# Test weak password
success, errors = authentication.register_user(
    "Jane Tan",
    "janetan123",
    "abc123"
)

print(success)
assert errors == [
    "* Must contain at least 12 characters.",
    "* Must contain at least 1 uppercase letter",
    "* Must contain at least 1 symbol"
]

# Verify account not save in DB
user = database.get_user_by_username("janetan123")

print(user)

# Current user after failed login
database.get_user_by_username("samdenby123").activate_account()

authentication.login("samdenby123", "Singapore2026!")

authentication.login("samdenby123", "WrongPassword123!")

print(authentication.get_current_user())

# Logging in stores user
authentication.login("samdenby123", "Singapore2026!")

current_user = authentication.get_current_user()

print(current_user.get_username())
print(current_user.get_user_id())
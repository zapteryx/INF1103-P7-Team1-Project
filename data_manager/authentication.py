from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from .user_manager import User, UserManager

# Maintained by Mahima (2604701)
# Maintained by Ming Xuan (2604426)
class Authentication:
    """
    Handles user authentication, registration, and session management.
    Uses Argon2 for secure password hashing.
    """

    def __init__(self, user_manager: UserManager) -> None:
        """
        Initialize authentication system with a UserManager instance.

        Args:
            user_manager: UserManager instance for database operations
        """
        self.__current_user: User | None = None
        self.__password_hasher = PasswordHasher()
        self.__user_manager = user_manager

    # Maintained by Mahima (2604701)
    def is_username_available(self, username: str) -> bool:
        """
        Check if a username is available for registration.

        Args:
            username: Username to check

        Returns:
            True if username is available, False if already taken
        """
        user = self.__user_manager.get_user_by_username(username)
        return user is None

    # Maintained by Mahima (2604701)
    def check_password_strength(self, password: str) -> list[str]:
        """
        Validate password strength against security requirements.

        Requirements:
        - At least 12 characters
        - At least 1 uppercase letter
        - At least 1 lowercase letter
        - At least 1 digit
        - At least 1 symbol

        Args:
            password: Password to validate

        Returns:
            List of error messages (empty if password is strong)
        """
        errors = []

        if len(password) < 12:
            errors.append("* Must contain at least 12 characters.")

        contains_uppercase = False
        contains_lowercase = False
        contains_digit = False
        contains_symbol = False

        for each_char in password:
            if each_char.isupper():
                contains_uppercase = True
            if each_char.islower():
                contains_lowercase = True
            if each_char.isdigit():
                contains_digit = True
            if not each_char.isalnum() and not each_char.isspace():
                contains_symbol = True

        if not contains_uppercase:
            errors.append("* Must contain at least 1 uppercase letter")

        if not contains_lowercase:
            errors.append("* Must contain at least 1 lowercase letter")

        if not contains_digit:
            errors.append("* Must contain at least 1 numerical digit")

        if not contains_symbol:
            errors.append("* Must contain at least 1 symbol")

        return errors

    # Maintained by Mahima (2604701)
    def passwords_match(self, password: str, confirm_password: str) -> bool:
        """
        Check if password and confirmation match.

        Args:
            password: Original password
            confirm_password: Confirmation password

        Returns:
            True if passwords match, False otherwise
        """
        return password == confirm_password

    # Maintained by Mahima (2604701)
    def register_user(
        self,
        name: str,
        username: str,
        password: str
    ) -> tuple[bool, list[str]]:
        """
        Register a new user account.

        Args:
            name: User's full name
            username: Desired username
            password: User's password

        Returns:
            Tuple of (success: bool, errors: list[str])
        """
        if not self.is_username_available(username):
            return False, ["Username already exists."]

        password_errors = self.check_password_strength(password)
        if password_errors:
            return False, password_errors

        password_hash = self.__password_hasher.hash(password)

        user_id = self.__user_manager.create_user(name, username, password_hash)

        if user_id is not None:
            return True, []
        else:
            return False, ["Unable to create an account."]

    # Maintained by Mahima (2604701)
    def login(self, username: str, password: str) -> tuple[bool, str]:
        """
        Authenticate a user and start a session.

        Args:
            username: User's username
            password: User's password

        Returns:
            Tuple of (success: bool, message: str)
        """
        self.__current_user = None

        user = self.__user_manager.get_user_by_username(username)

        if user is None:
            return False, "Invalid username or password"

        try:
            self.__password_hasher.verify(user.password_hash, password)
        except VerifyMismatchError:
            return False, "Invalid username or password"

        if not user.is_active:
            return False, "Account is inactive"

        self.__current_user = user
        return True, f"Welcome, {user.name}!"

    # Maintained by Mahima (2604701)
    def logout(self) -> None:
        """Clear the current user session."""
        self.__current_user = None

    # Maintained by Mahima (2604701)
    def get_current_user(self) -> User | None:
        """
        Get the currently logged-in user.

        Returns:
            User object if logged in, None otherwise
        """
        return self.__current_user

    # Maintained by Mahima (2604701)
    def is_logged_in(self) -> bool:
        """
        Check if a user is currently logged in.

        Returns:
            True if user is logged in, False otherwise
        """
        return self.__current_user is not None

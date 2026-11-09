from argon2 import PasswordHasher

class Authentication:
    # No user logged in
    def __init__(self, database):
        self.__current_user = None
        self.__password_hasher = PasswordHasher()
        self.__database = database

    # Need to retrieve from DB to check whether username alr exists (Unique)
    def is_username_available(self, username):
        user = self.__database.get_user_by_username(username)
        if user is None:
            return True
        else:
            return False
    
    # Function called into I/O for user to know why password isn't accepted (Must be strong)
    def check_password_strength(self, password):
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

        if contains_uppercase == False:
            errors.append("* Must contain at least 1 uppercase letter")

        if contains_lowercase == False:
            errors.append("* Must contain at least 1 lowercase letter")

        if contains_digit == False:
            errors.append("* Must contain at least 1 numerical digit")

        if contains_symbol == False:
            errors.append("* Must contain at least 1 symbol")

        return errors

    def passwords_match(self, password, confirm_password):
        return password == confirm_password
        # Returns True or False

    def register_user(self, name, username, password):
        if self.is_username_available(username) is False:
            return False, ["Username already exists."]

        password_errors = self.check_password_strength(password)
        if password_errors:
            return False, password_errors

        password_hash = self.__password_hasher.hash(password)

        user_id = self.__database.create_user(name, username, password_hash)

        if user_id is not None:
            return True, []
        
        else:
            return False, ["Unable to create an account."]

    def login(self, username, password):
        pass
        


    def logout(self):
        self.__current_user = None
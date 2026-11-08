class User:
    def __init__(self, user_id, name, username, password_hash, registration_date, account_status = True):
        self.__user_id = user_id
        self.__name = name
        self.__username = username
        self.__password_hash = password_hash
        self.__registration_date = registration_date
        self.__account_status = account_status

    # Getters to access private user info
    def get_user_id(self):
        return self.__user_id

    def get_name(self):
        return self.__name

    def get_username(self):
        return self.__username

    def get_password_hash(self):
        return self.__password_hash

    def get_registration_date(self):
        return self.__registration_date
    
    def get_account_status(self):
        return self.__account_status

    # Account status management methods: True or False
    def activate_account(self):
        self.__account_status = True

    def deactivate_account(self):
        self.__account_status = False
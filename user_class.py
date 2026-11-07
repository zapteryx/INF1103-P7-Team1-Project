class User:
    def __init__(self, user_id, username, password_hash, recovery_email, recovery_phone, registration_date, account_status = True):
        self.__user_id = user_id
        self.__username = username
        self.__password_hash = password_hash
        self.__recovery_email = recovery_email
        self.__recovery_phone = recovery_phone
        self.__registration_date = registration_date
        self.__account_status = account_status

    def get_user_id(self):
        return self.__user_id

    def get_username(self):
        return self.__username

    def get_password_hash(self):
        return self.__password_hash

    def get_recovery_email(self):
        return self.__recovery_email

    def get_recovery_phone(self):
        return self.__recovery_phone

    def get_registration_date(self):
        return self.__registration_date
    
    def get_account_status(self):
        return self.__account_status
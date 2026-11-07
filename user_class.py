class User:
    def __init__(self, user_id, username, password_hash, recovery_email, recovery_phone, registration_date, account_status):
        self.__user_id = user_id
        self.__username = username
        self.__password_hash = password_hash
        self.__recovery_email = recovery_email
        self.__recovery_phone = recovery_phone
        self.__registration_date = registration_date
        self.__account_status = account_status
        
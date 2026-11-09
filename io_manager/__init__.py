import sys
from abc import ABC, abstractmethod
from data_manager import ShelterFileReader, FileValidator


class ShelterBase(ABC):
    """defining the contract for shelter data representations."""

    def __init__(self, data: dict):
        self.data = data

    @abstractmethod
    def format_details(self) -> str:
        pass


class CsvShelter(ShelterBase):
    """Represents a standard CSV-loaded shelter record."""

    def format_details(self) -> str:
        name = self.data.get("name", "N/A")
        category = self.data.get("category", "N/A")
        requirements = self.data.get("requirements", "N/A")
        capacity = int(self.data.get("capacity", 0))
        occupants = int(self.data.get("occupants", 0))
        available = max(0, capacity - occupants)
        contact = self.data.get("contact", "N/A")

        info = ""
        info += f"Name:   {name}\n"
        info += f"Category:   {category}\n"
        info += f"Requirements:   {requirements}\n"
        info += f"Available:   {available} bed left ({occupants}/{capacity} occupied)\n"
        info += f"Contact:     {contact}"
        return info

class AIShelter(ShelterBase):
    """Represents an AI-manager-generated shelter recommendation record."""

    def format_details(self) -> str:
        rank = self.data.get("rank", "N/A")
        name = self.data.get("shelter_name", "N/A")
        ai_score = self.data.get("ai_suitability_score", "N/A")
        ai_conf = self.data.get("ai_confidence_score", "N/A")
        min_age = self.data.get("min_age", "N/A")
        max_age = self.data.get("max_age", "N/A")
        gender = self.data.get("gender_restriction", "N/A")
        dependents_allowed = self.data.get("dependents_allowed", False)
        dependents_status = "Allowed" if dependents_allowed else "Not Allowed"

        info = ""
        info += f"Rank       : {rank}\n"
        info += f"Name       : {name}\n"
        info += f"AI Score   : {ai_score}\n"
        info += f"AI Conf.   : {ai_conf}\n"
        info += f"Age Group  : {min_age} - {max_age}\n"
        info += f"Gender     : {gender}\n"
        info += f"Dependents : {dependents_status}"
        return info

class IOManager:
    @staticmethod
    def print_error(err_title: str, err_desc: str = "") -> None:
        desc_str = f": {err_desc}" if err_desc else ""
        print(f"Encountered an error:\n{err_title}{desc_str}", file=sys.stderr)

    @staticmethod
    def print_update(update_title: str, update_desc: str = "") -> None:
        desc_str = f": {update_desc}" if update_desc else ""
        print(f"{update_title}{desc_str}")

    @staticmethod
    def display_auth_menu() -> int:
        print("\n====================================")
        print("    ShelterFlow AI - Access Portal  ")
        print("====================================")
        print("1. Register")
        print("2. Login")
        print("3. Exit System")
        print("====================================")
        choice_input = input("Select option (1-3): ").strip()

        while not choice_input.isdigit() or int(choice_input) not in range(1, 4):
            print("Invalid option. Please enter a number between 1 and 3.")
            choice_input = input("Select option (1-3): ").strip()
        return int(choice_input)

    @staticmethod
    def collect_registration_input(existing_usernames: list = None) -> dict:
        """
        Collects user registration inputs (name, username, password, confirm_password).
        Validates non-empty fields, username uniqueness, and password matching with retry loops.
        """
        if existing_usernames is None:
            existing_usernames = []

        print("\n--- ACCOUNT REGISTRATION ---")
        
        name = input("Enter Full Name: ").strip()
        while not name:
            print("[!] Name cannot be empty.")
            name = input("Enter Full Name: ").strip()

        username = input("Enter Username: ").strip()
        while not username or username.lower() in [u.lower() for u in existing_usernames]:
            if not username:
                print("[!] Username cannot be empty.")
            else:
                print("[!] Username already taken. Please choose another username.")
            username = input("Enter Username: ").strip()

        while True:
            password = input("Enter Password: ").strip()
            while not password:
                print("[!] Password cannot be empty.")
                password = input("Enter Password: ").strip()

            confirm_password = input("Confirm Password: ").strip()

            if password == confirm_password:
                print("[✓] Passwords match successfully.")
                break
            else:
                print("[!] Registration Error: Passwords do not match. Please try again.\n")

        return {
            "name": name,
            "username": username,
            "password": password
        }
    
    @staticmethod
    def get_shelter_filename(default_filename: str = "singapore_shelters_directory.csv") -> str:
        print(f"\nDefault dataset: '{default_filename}'")
        while True:
            filename = input("Enter shelter CSV filename (or press Enter for default): ").strip()
            if not filename:
                filename = default_filename
            validation = FileValidator.validate_csv_filename(filename)
            if validation[0]:
                break
            print(f"Error: {validation[1]}")
        return filename

    @staticmethod
    def get_client_records_filename(accepted_filetypes: list, allow_creating_new: bool = False, default_filename: str = "clients.json") -> str:
        print(f"\nDefault dataset: '{default_filename}'")
        while True:
            filename = input(f"Enter client records filename ({'/'.join(accepted_filetypes).upper()}) (or press Enter for default): ").strip()
            if not filename:
                filename = default_filename
            if 'csv' in accepted_filetypes and filename.endswith('.csv'):
                validation = FileValidator.validate_csv_filename(filename)
                if validation[0] or (validation[1] == "CSV file not found." and allow_creating_new):
                    break
                print(f"Error: {validation[1]}")
                continue
            if 'json' in accepted_filetypes and filename.endswith('.json'):
                validation = FileValidator.validate_json_filename(filename)
                if validation[0] or (validation[1] == "JSON file not found." and allow_creating_new):
                    break
                print(f"Error: {validation[1]}")
                continue
            print(f"Error: The provided file format is not accepted. Please provide a {'/'.join(accepted_filetypes).upper()} file.")
        return filename

    @staticmethod
    def format_shelter(shelter: dict | ShelterBase) -> str:
        """Polymorphically formats any shelter input (dictionary or object)."""
        if isinstance(shelter, ShelterBase):
            shelter_obj = shelter
        elif isinstance(shelter, dict):
            # Automatically route to the correct subclass based on dictionary keys
            if "shelter_name" in shelter:
                shelter_obj = AIShelter(shelter)
            else:
                shelter_obj = CsvShelter(shelter)
        else:
            return "Invalid shelter data format."

        return shelter_obj.format_details() + "\n------------------------------------------------------"

    @staticmethod
    def print_shelter_list(shelters: list) -> None:
        if not shelters:
            print("\nNo shelters available to display.")
            return

        print("\n===== AVAILABLE SHELTERS =====\n")
        for shelter in shelters:
            print(IOManager.format_shelter(shelter))

    @staticmethod
    def display_menu() -> int:
        print("====================================")
        print("         Social Service AI          ")
        print("====================================")
        print("1. New Client Intake")
        print("2. View All Shelters")
        print("3. Get Shelter recommendations for clients")
        print("4. Search Client by NRIC")
        print("5. Filter Cases by Outcome")
        print("6. Exit")
        print("====================================")
        choice_input = input("Select option (1-6): ").strip()

        while not choice_input.isdigit() or int(choice_input) not in range(1, 7):
            print("Invalid option. Please enter a number between 1 and 6.")
            choice_input = input("Select option (1-6): ").strip()
        return int(choice_input)

    @staticmethod
    def collect_intake_input() -> dict:
        print("\n--- NEW CLIENT INTAKE---")

        # Client ID Input & NRIC Validation
        client_id = input("Enter NRIC: ").strip().upper()
        is_valid_nric = (
            len(client_id) == 9
            and client_id[0] in ["S", "T"]
            and client_id[1:8].isdigit()
            and client_id[-1].isalpha()
        )

        while not is_valid_nric:
            print("Invalid NRIC. Must start with S or T, followed by 7 digits and end with a letter (eg; S1234567H)")
            client_id = input("Enter NRIC: ").strip().upper()
            is_valid_nric = (
                len(client_id) == 9
                and client_id[0] in ["S", "T"]
                and client_id[1:8].isdigit()
                and client_id[-1].isalpha()
            )

        # Gender Input & Validation
        gender_input = input("Enter Client Gender (Male / Female): ").strip().lower()
        while gender_input not in ["male", "female", "m", "f"]:
            print("Invalid input. Please enter 'Male' or 'Female'.")
            gender_input = input("Enter Client Gender (Male / Female): ").strip().lower()
        gender = "Male" if gender_input in ["male", "m"] else "Female"

        # Age Input & Validation (Capped at 125)
        age_input = input("Enter Client Age: ").strip()
        while not age_input.isdigit() or not (1 <= int(age_input) <= 125):
            print("Please enter a valid number for age between 1 and 125.")
            age_input = input("Enter Client Age: ").strip()
        age = int(age_input)

        # Dependents Input & Validation (Capped at 20)
        dep_input = input("Enter Number of Dependents: ").strip()
        while not dep_input.isdigit() or not (0 <= int(dep_input) <= 20):
            print("Please enter a valid number for dependents (cap at 20).")
            dep_input = input("Enter Number of Dependents: ").strip()
        dependents = int(dep_input)

        # Type of Care Input & Validation
        care_input = input("Type of care required (Short Term / Long Term): ").strip().lower()
        while care_input not in ["short term", "long term", "short", "long"]:
            print("Invalid input. Please enter Short Term or Long Term.")
            care_input = input("Type of care required (Short Term / Long Term): ").strip().lower()
        care_type = "Short Term" if "short" in care_input else "Long Term"

        # Special Needs Input & Validation
        needs_input = input("Special Needs (Yes / No): ").strip().lower()
        while needs_input not in ["yes", "no", "y", "n"]:
            print("Invalid input. Please enter 'Yes' or 'No'.")
            needs_input = input("Special Needs (Yes / No): ").strip().lower()
        special_needs = "Yes" if needs_input in ["yes", "y"] else "No"

        # Intake Description / Notes Inputs
        intakes_notes = input("Enter intake description: ").strip()

        return {
            "client_id": client_id,
            "gender": gender,
            "age": age,
            "dependents": dependents,
            "care_type": care_type,
            "special_needs": special_needs,
            "intakes_notes": intakes_notes
        }

    @staticmethod
    def ask_for_client_id() -> str:
        print("\n---CLIENT SEARCH---")
        client_id = input("Enter Client NRIC: ").strip().upper()

        is_valid_nric = (
            len(client_id) == 9
            and client_id[0] in ["S", "T"]
            and client_id[1:8].isdigit()
            and client_id[-1].isalpha()
        )

        while not is_valid_nric:
            print("Invalid NRIC. Must start with S or T, followed by 7 digits and end with a letter (eg; S1234567H)")
            client_id = input("Enter Client NRIC: ").strip().upper()
            is_valid_nric = (
                len(client_id) == 9
                and client_id[0] in ["S", "T"]
                and client_id[1:8].isdigit()
                and client_id[-1].isalpha()
            )

        return client_id

    @staticmethod
    def present_best_shelter(client: dict, shelter) -> bool:
        print("\n======== RECOMMENDED MATCH ========")
        print(f"Client ID: {client.get('client_id', 'N/A')}")
        print(f"Care Type: {client.get('care_type', 'N/A')}")
        print("-------------------------------------")

        if not shelter:
            print("No suitable shelter found matching the client criteria")
            return False
        print("Suggested Shelter Details: ")
        print(IOManager.format_shelter(shelter))

        choice = input("\nDo you accept this shelter outcome? (Yes / No): ").strip().lower()
        while choice not in ["yes", "no", "y", "n"]:
            print("Invalid input. please enter 'Yes' or 'No'.")
            choice = input("Do you accept this shelter outcome (Yes / No): ").strip().lower()
        return choice in ["yes", "y"]

    @staticmethod
    def print_client_record(client: dict) -> None:
        print("\n=================== CLIENT RECORD ===================")
        print(f"Client ID     : {client.get('client_id', 'N/A')}")
        print(f"Gender        : {client.get('gender', 'N/A')}")
        print(f"Age           : {client.get('age', 'N/A')}")
        print(f"Dependents    : {client.get('dependents', 'N/A')}")
        print(f"Care Type     : {client.get('care_type', 'N/A')}")
        print(f"Special Needs : {client.get('special_needs', 'N/A')}")
        print(f"Notes         : {client.get('intakes_notes', 'N/A')}")

        outcome = client.get("outcome")
        accepted_shelter = client.get("accepted_shelter")

        if outcome is True and accepted_shelter:
            print("\n[Status] Outcome: Accepted")
            print(IOManager.format_shelter(accepted_shelter))
        elif outcome is False:
            print("\n[Status] Outcome: Rejected")
        else:
            print("\n[Status] Outcome: Pending")
        print("=====================================================")

    @staticmethod
    def get_rerun_decision() -> bool:
        choice = input("\nWould you like to rerun the AI matching for this client? (Yes / No): ").strip().lower()
        while choice not in ["yes", "no", "y", "n"]:
            print("[!] Invalid input. Please enter 'Yes' or 'No'.")
            choice = input("Would you like to rerun the AI matching for this client? (Yes / No): ").strip().lower()
        return choice in ["yes", "y"]

    @staticmethod
    def ask_for_outcome_filter() -> bool | None:
        print("\n--- FILTER CASES BY OUTCOME ---")
        print("Options: Accepted, Rejected, Pending")

        while True:
            outcome = input("Enter outcome to filter by: ").strip().lower()

            if not outcome:
                print("Outcome cannot be empty. Please enter a valid outcome.")
                continue

            if outcome in ['accepted', 'accept', 'yes', 'true']:
                return True
            elif outcome in ['rejected', 'reject', 'no', 'false']:
                return False
            elif outcome in ['pending', 'none', 'empty']:
                return None
            else:
                print(f"Invalid outcome '{outcome}'. Please enter: Accepted, Rejected, or Pending.")
                continue

    @staticmethod
    def print_filtered_cases(cases: list, outcome: bool | None) -> None:
        if outcome is True:
            outcome_display = "Accepted"
        elif outcome is False:
            outcome_display = "Rejected"
        else:
            outcome_display = "Pending"

        if not cases:
            print(f"\nNo cases found with outcome: {outcome_display}")
            return

        print(f"\n===== CASES WITH OUTCOME: {outcome_display} =====")
        print(f"Total cases found: {len(cases)}\n")

        for case in cases:
            IOManager.print_client_record(case)
            print()

__all__ = ["IOManager", "ShelterBase", "CsvShelter", "AIShelter"]
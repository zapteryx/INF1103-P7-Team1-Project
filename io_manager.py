import csv
import os

import data_manager

# Maintained by Shi Ting (2600663)
# Modified by Ming Xuan (2604426)
def get_shelter_filename(default_filename: str = "singapore_shelters_directory.csv") -> str:
    # Prompts the user to enter the shelter dataset filename.
    # Allows pressing Enter to use the default filename and validates file existence.
    print(f"\nDefault dataset: '{default_filename}'")
    while True:
        filename = input("Enter shelter CSV filename (or press Enter for default): ").strip()
        # Use default if user presses Enter without typing anything
        if not filename:
            filename = default_filename
        validation = data_manager.validate_csv_filename(filename)
        if validation[0]:
            break
        print(f"Error: {validation[1]}")
    return filename

def get_client_records_filename (default_filename: str = "clients.json") -> str:
    # Prompts the user to enter the client records filename.
    # Allows pressing Enter to use the default filename and validates file existence.
    print(f"\nDefault dataset: '{default_filename}'")
    while True:
        filename = input("Enter client records filename (CSV/JSON) (or press Enter for default): ").strip()
        # Use default if user presses Enter without typing anything
        if not filename:
            filename = default_filename
        validation = data_manager.validate_csv_filename(filename)
        if validation[0]:
            break
        validation = data_manager.validate_json_filename(filename)
        # If the file is not found, break the loop to allow the user to create a new file
        if validation[0] or validation[1] == "JSON file not found.":
            break
        print(f"Error: {validation[1]}")
    return filename

# Maintained by Shi Ting (2600663)
# Terminal Display & Formatting
def format_shelter(shelter: dict) -> str:  #Is a hint stating that this input must be a dictionary and this functions returns a string
    info = ""
    info += "Name:   " + shelter["name"] + "\n"
    info += "Category:   " + shelter["category"] + "\n"
    info += "Requirements:   " + shelter["requirements"] + "\n"
    info += "Available:   " + str(shelter["capacity"] - shelter["occupants"]) + " bed left (" + str(shelter["occupants"]) + "/" + str(shelter["capacity"]) + " occupied)\n"
    info += "Contact:     " + shelter["contact"] + "\n"
    info += "------------------------------------------------------"
    return info

# Maintained by Shi Ting (2600663)
def print_shelter_list(shelters: list) -> None: # :list is a type hint stating this parameter expects a Python list
    if not shelters:                            #  None -> returns nothing
        print("\nNo shelters available to display.")
        return

    print("\n===== AVAILABLE SHELTERS =====\n")
    for shelter in shelters:
        print(format_shelter(shelter))

# Maintained by Shi Ting (2600663)
def display_menu() -> int: #Is a hint stating that the function returns an integer
    print("====================================")
    print("         Social Service AI          ")
    print("====================================")
    print("1. New Client Intake")
    print("2. View All Shelters")
    print("3. Update CSV/JSON File Used")
    print("4. Get Shelter recommendations for clients")
    print("5. Exit")
    print("====================================")
    choice_input = input("Select option (1-5): ").strip() #.strip removes leading and trailing whitespace eg; space, tabs or newline characters

    #Validate Input Menu Options
    while not choice_input.isdigit():
        print("Invalid option. Please enter a number between 1 and 5.")
        choice_input = input("Select option (1-5): ").strip()
    return int(choice_input)

# Maintained by Shi Ting (2600663)
# User input collection & Validation
def collect_intake_input() -> dict:
    print("\n--- NEW CLIENT INTAKE---")

    # Client ID Input & Validation
    client_id = input("Enter NRIC: ").strip()
    while not client_id:
        print("Client ID cannot be empty.")
        client_id = input("Enter NRIC: ").strip()

    # Gender Input & Validation (Male / Female)
    gender_input = input("Enter Client Gender (Male / Female): ").strip().lower()
    while gender_input not in ["male", "female", "m", "f"]:
        print("Invalid input. Please enter 'Male' or 'Female'.")
        gender_input = input("Enter Client Gender (Male / Female): ").strip().lower()

    gender = "Male" if gender_input in ["male", "m"] else "Female"

    #Age Input & Validation
    age_input = input("Enter Client Age: ").strip()
    while not age_input.isdigit():
        print("Please enter a valid number for age.")
        age_input = input("Enter Client Age: ").strip()
    age = int(age_input)

    # Dependents Input & Validation
    dep_input = input("Enter Number of Dependents: ").strip()
    while not dep_input.isdigit():
        print("Please enter a valid number for dependents.")
        dep_input = input("Enter Number of Dependents: ").strip()
    dependents = int(dep_input)

    #Type of Care Input & Validation (Short Term / Long Term)
    care_input = input("Type of care required (Short Term / Long Term): ").strip().lower() #.lower() help to convert any uppercase to lowercase
    while care_input not in ["short term", "long term", "short", "long"]:
        print("Invalid input. Please enter Short Term or Long Term.")
        care_input = input("Type of care required (Short Term / Long Term): ").strip().lower()

    if "short" in care_input:  #Standardize care output text
        care_type = "Short Term"
    else:
        care_type = "Long Term"

    #Special Needs Input & Validation (Yes / No)
    needs_input = input("Special Needs (Yes / No): ").strip().lower()
    while needs_input not in ["yes", "no", "y", "n"]:
        print("Invalid input. Please enter 'Yes' or 'No'.")
        needs_input = input("Special Needs (Yes / No): ").strip().lower()

    special_needs = "Yes" if needs_input in ["yes", "y"] else "No"  #Standardize special needs output text

    #Intake Description / Notes Inputs
    intakes_notes = input("Enter intake description: ").strip()

    return {
        "client_id": client_id,
        "gender": gender,
        "age": age,
        "dependents": dependents,
        "care_type": care_type,
        "special_needs": special_needs,
        "intake_notes": intakes_notes
    }
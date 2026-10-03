import csv
import os

FILENAME = "singapore_shelters_directory.csv"

# Maintained by Shi Ting (2600663)
def get_shelter_filename(default_filename: str = FILENAME) -> str:
    # Prompts the user to enter the shelter dataset filename.
    # Allows pressing Enter to use the default filename and validates file existence.

    print(f"\nDefault dataset: '{default_filename}'")
    filename = input("Enter shelter CSV filename (or press Enter for default): ").strip()

    # Use default if user presses Enter without typing anything
    if not filename:
        filename = default_filename

    # Validation loop: Check if the file actually exists on disk
    while not os.path.exists(filename):
        print(f"[!] File '{filename}' not found. Please make sure the path and filename are correct.")
        filename = input("Enter shelter CSV filename (or press Enter for default): ").strip()
        if not filename:
            filename = default_filename

    return filename

# Maintained by Shi Ting (2600663)
# CSV Reading
def load_shelters_from_csv(filepath: str) -> list:
    shelters = []
# Translate raw binary binary bytes into readable text characters . utf-8 : is the standard character encoding for web and modern text files, sig stands for signature
    with open(filepath, mode="r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)   #Creates a special object that reads a CSV file line by line and automatically converts each row into a Python dictionary

        for row in reader:
            capacity = int(row.get ("Maximum Capacity", 0))   # It will replace the value if it can find else it will be 0 instead of crashing the entire application
            occupants = int(row.get("Current occupants", 0))

            available = capacity - occupants
            if available < 0:
                available = 0   # So that i won t have negative numbers

            accomodations = {
                "name": row.get("Shelter Name", "N/A"), #Looks up the "Shelter Name" column in the CSV. If found, it stores the name string else default as N/A
                "category": row.get("Category", "N/A"),
                "capacity": capacity,
                "occupants": occupants,
                "available": available,
                "requirements": row.get("Requirements", "N/A"),
                "contact": row.get("Contact", "N/A"),
                "location": row.get("Location", "N/A")
            }
            shelters.append(accomodations)
    return shelters

# Maintained by Shi Ting (2600663)
# Terminal Display & Formatting
def format_shelter(shelter: dict) -> str:  #Is a hint stating that this input must be a dictionary and this functions returns a string
    info = ""
    info += "Name:   " + shelter["name"] + "\n"
    info += "Category:   " + shelter["category"] + "\n"
    info += "Requirements:   " + shelter["requirements"] + "\n"
    info += "Available:   " + str(shelter["available"]) + " bed left (" + str(shelter["occupants"]) + "/" + str(shelter["capacity"]) + " occupied)\n"
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
    print("3. Update CSV File Used")
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

    # Client ID Validation
    client_id = input("Enter NRIC: ").strip()
    while not client_id:
        print("Client ID cannot be empty.")
        client_id = input("Enter NRIC: ").strip()

    #Age Validation
    age_input = input("Enter Client Age: ").strip()
    while not age_input.isdigit():
        print("Please enter a valid number for age.")
        age_input = input("Enter Client Age: ").strip()
    age = int(age_input)

    # Dependents Validation
    dep_input = input("Enter Number of Dependents: ").strip()
    while not dep_input.isdigit():
        print("Please enter a valid number for dependents.")
        dep_input = input("Enter Number of Dependents: ").strip()
    dependents = int(dep_input)

    #Type of Care Validation (Short Term / Long Term)
    care_input = input("Type of care required (Short Term / Long Term): ").strip().lower() #.lower() help to convert any uppercase to lowercase
    while care_input not in ["short term", "long term", "short", "long"]:
        print("Invalid input. Please enter Short Term or Long Term.")
        care_input = input("Type of care required (Short Term / Long Term): ").strip().lower()

    if "short" in care_input:  #Standardize care output text
        care_type = "Short Term"
    else:
        care_type = "Long Term"

    #Special Needs Validation (Yes / No)
    needs_input = input("Special Needs (Yes / No): ").strip().lower()
    while needs_input not in ["yes", "no", "y", "n"]:
        print("Invalid input. Please enter 'Yes' or 'No'.")
        needs_input = input("Special Needs (Yes / No): ").strip().lower()

    special_needs = "Yes" if needs_input in ["yes", "y"] else "No"  #Standardize special needs output text

    #Intake Description / Notes
    intakes_notes = input("Enter intake description: ").strip()

    return {
        "client_id": client_id,
        "age": age,
        "dependents": dependents,
        "care_type": care_type,
        "special_needs": special_needs,
        "intake_notes": intakes_notes
    }
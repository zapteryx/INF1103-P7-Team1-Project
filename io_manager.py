import csv
import os

filename = "singapore_shelters_directory.csv"

#CSV Reading
def load_shelters_from_csv(filepath: str = filename) -> list:
    #Reads shelter data directly from CSV into a list of dictionaries.
    if not os.path.exists(filepath):
        print("\nFile not found:", filepath) # the built-in os module that checks the path stored in filepath
        return []

    shelters = []

    with open(filepath, mode="r", encodings="utf-8-sig") as file: # Translate raw binary binary bytes into readable text characters . utf-8 : is the standard character encoding for web and modern text files, sig stands for signature 
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
    return accomodations 

# Terminal Display & Formatting
def format_shelter(shelter: dict) -> str:  #Is a hint stating that this input must be a dictionary and this functions returns a string
    info = ""
    info += "Name:   " + shelter["name"] + "\n"
    info += "Category:   " + shelter["category"] + "\n"
    info += "Target:   " + shelter["target"] + "\n"
    info += "Available:   " + str(shelter["available"]) + "bed left (" + str(shelter["occupants"]) + "/" + str(shelter["capacity"]) + " occupied)\n"
    info += "Contact:     " + shelter["contact"] + "\n"
    info += "------------------------------------------------------"
    return info

def print_shelter_list(shelters: list) -> None: # :list is a type hint stating this parameter expects a Python list
    if not shelters:                            #  None -> returns nothing
        print("\nNo shelters available to display.")
        return
    
    print("\n===== AVAILABLE SHELTERS =====\n")
    for shelter in shelters:
        print(format_shelter(shelter))

def display_menu() -> str: #Is a hint stating that the function returns a string
    print("\n==================================")
    print("         Social Service AI          ")
    print("====================================")
    print("1. New Client Intake")
    print("2. View All Shelters")
    print("3. Exit")
    print("====================================")
    choice = input("Select option (1-3): ")
    return choice.strip()   #.strip removes leading and trailing whitespace eg; space, tabs or newline characters

# User input collection & Validation
def collect_intake_input() -> dict:
    print("\n--- NEW CLIENT INTAKE---")

    #Client ID Validation
    client_id = input("Enter Client ID: ").strip()
    while not client_id:
        print("Client ID cannot be empty")
        client_id = input("Enter Client ID: ").strip()
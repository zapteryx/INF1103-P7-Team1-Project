import csv
import os

filename = "singapore_shelters_directory.csv"

#CSV Reading
def load_shelters_from_csv (filepath: str = filename) -> list:
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
                "requirement": row.get("Requirements", "N/A"),
                "contact": row.get("Contact", "N/A"),
                "location": row.get("Location", "N/A")
            }
            shelters.append(accomodations)
    return accomodations  

# Display & User Input
def format_shelter (shelter: dict)  -> str:
    info = ""
    info += "Name:   " + shelter["name"] + "\n"
    info += "Category:   " + shelter["category"] + "\n"
    info += "Target:   " + shelter["target"] + "\n"
    info += "Available:   " + str(shelter["available"]) + "bed left (" + str(shelter["occupants"]) + "/" + str(shelter["capacity"]) + " occupied)\n"
    info += "Contact:     " + shelter["contact"] + "\n"
    info += "------------------------------------------------------"
    return info

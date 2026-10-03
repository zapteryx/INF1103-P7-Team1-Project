import json
import csv

# Maintained by Htet Shine Aung (2604711)
# Load case record from JSON or CSV file
def load_records(filename):
    cases = []

    try:
        # Load JSON file
        if filename.lower().endswith(".json"):
            with open(filename, "r", encoding="utf-8") as file:
                cases = json.load(file)

            # Make sure the JSON contains a list
            if not isinstance(cases, list):
                return [], "The JSON file must contain a list of cases."

            # Make sure each case is a dictionary
            for case in cases:
                if not isinstance(case, dict):
                    return [], "A case in the file has an invalid format."

        # Load CSV file
        elif filename.lower().endswith(".csv"):
            with open(filename, "r", encoding="utf-8-sig") as file:
                reader = csv.DictReader(file)

                for row in reader:
                    case = {
                        "client_id": row.get("client_id", ""),
                        "age": int(row.get("age", 0)),
                        "dependents": int(row.get("dependents", 0)),
                        "care_type": row.get("care_type", ""),
                        "special_needs": row.get("special_needs", ""),
                        "intake_notes": row.get("intake_notes", "")
                    }

                    cases.append(case)

        # Not JSON or CSV
        else:
            return [], "File must be a JSON or CSV file."

        return cases, None

    except FileNotFoundError:
        return [], "File not found."

    except json.JSONDecodeError:
        return [], "The JSON file is invalid."

    except (OSError, UnicodeDecodeError, ValueError, csv.Error):
        return [], "Unable to read the file."


# Maintained by Htet Shine Aung (2604711)
# Save case records to JSON file
def save_records(filename, records):
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(records, file, indent=4)

        return True, None

    except OSError:
        return False, "Unable to save records."


# Maintained by Htet Shine Aung (2604711)
# Check if the selected file is a valid CSV file
def validate_csv_filename(filename):

    if not filename.lower().endswith(".csv"):
        return False, "Invalid file format. Please select a CSV file."

    try:
        with open(filename, "r", encoding="utf-8-sig") as file:
            reader = csv.reader(file)

            # Check if the file has a header
            header = next(reader, None)

            if header is None:
                return False, "The selected CSV file does not have a valid header."

        return True, None

    except FileNotFoundError:
        return False, "CSV file not found."

    except (OSError, csv.Error, UnicodeDecodeError):
        return False, "Unable to read the CSV file."


# Maintained by Htet Shine Aung (2604711)
# Load shelters from CSV file
def load_shelters(filename):
    shelters = []

    # Check the file first
    valid, error = validate_csv_filename(filename)

    if not valid:
        return [], error

    try:
        with open(filename, "r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            for row in reader:
                capacity = int(row.get("Maximum Capacity", 0))
                occupants = int(row.get("Current Occupants", 0))

                shelter = {
                    "name": row.get("Shelter Name", "N/A"),
                    "category": row.get("Category", "N/A"),
                    "capacity": capacity,
                    "occupants": occupants,
                    "requirements": row.get("Requirements", "N/A"),
                    "contact": row.get("Contact", "N/A"),
                    "location": row.get("Address", "N/A")
                }

                shelters.append(shelter)

        return shelters, None

    except FileNotFoundError:
        return [], "CSV file not found."

    except (OSError, ValueError, csv.Error):
        return [], "Unable to load shelter data."

# Maintained by Htet Shine Aung (2604711)
# Filter processed records by the outcome
def filter_records_by_outcome(records, outcome):
    filtered_records = []

    for record in records:
        if record.get("outcome", "").lower() == outcome.lower():
            filtered_records.append(record)

    return filtered_records
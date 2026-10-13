import json
import csv

# Maintained by Htet Shine Aung (2604711)
# Modified by Ming Xuan (2604426)
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
            # Define shelter field mapping for reconstruction
            shelter_fields = {
                "accepted_shelter_rank": "rank",
                "accepted_shelter_name": "shelter_name",
                "accepted_shelter_ai_score": "ai_suitability_score",
                "accepted_shelter_calc_score": "calculated_suitability_score",
                "accepted_shelter_confidence": "ai_confidence_score",
                "accepted_shelter_min_age": "min_age",
                "accepted_shelter_max_age": "max_age",
                "accepted_shelter_gender": "gender_restriction",
                "accepted_shelter_dependents": "dependents_allowed"
            }

            with open(filename, "r", encoding="utf-8-sig") as file:
                reader = csv.DictReader(file)

                for row in reader:
                    case = {
                        "client_id": row.get("client_id", ""),
                        "gender": row.get("gender", ""),
                        "age": int(row.get("age", 0)),
                        "dependents": int(row.get("dependents", 0)),
                        "care_type": row.get("care_type", ""),
                        "special_needs": row.get("special_needs", ""),
                        "intake_notes": row.get("intake_notes", ""),
                        "outcome": row.get("outcome", ""),
                    }

                    # Reconstruct accepted_shelter if name field exists
                    if row.get("accepted_shelter_name"):
                        accepted_shelter = {}
                        for flat_key, orig_key in shelter_fields.items():
                            value = row.get(flat_key, "")
                            if value:
                                if orig_key in ["ai_suitability_score", "calculated_suitability_score", "ai_confidence_score"]:
                                    accepted_shelter[orig_key] = float(value)
                                elif orig_key in ["min_age", "max_age"]:
                                    accepted_shelter[orig_key] = int(value)
                                elif orig_key == "dependents_allowed":
                                    accepted_shelter[orig_key] = value.lower() == "true"
                                else:
                                    accepted_shelter[orig_key] = value

                        if accepted_shelter:
                            case["accepted_shelter"] = accepted_shelter

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
# Modified by Ming Xuan (2604426)
# save/replace the WHOLE list
def save_records(filename, records):
    try:
        if filename.lower().endswith(".json"):
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(records, file, indent=4)

        elif filename.lower().endswith(".csv"):
            if not records:
                return False, "Cannot save an empty CSV without headers."

            # Define accepted_shelter field mapping for flattening
            shelter_fields = {
                "rank": "accepted_shelter_rank",
                "shelter_name": "accepted_shelter_name",
                "ai_suitability_score": "accepted_shelter_ai_score",
                "calculated_suitability_score": "accepted_shelter_calc_score",
                "ai_confidence_score": "accepted_shelter_confidence",
                "min_age": "accepted_shelter_min_age",
                "max_age": "accepted_shelter_max_age",
                "gender_restriction": "accepted_shelter_gender",
                "dependents_allowed": "accepted_shelter_dependents"
            }

            # Flatten nested accepted_shelter dict for CSV compatibility
            flattened_records = []
            for record in records:
                flat_record = {k: v for k, v in record.items() if k != "accepted_shelter"}

                # Flatten accepted_shelter if it exists
                accepted_shelter = record.get("accepted_shelter")
                if accepted_shelter and isinstance(accepted_shelter, dict):
                    for orig_key, flat_key in shelter_fields.items():
                        value = accepted_shelter.get(orig_key, "")
                        flat_record[flat_key] = str(value) if orig_key == "dependents_allowed" else value
                else:
                    # Add empty columns for consistency
                    for flat_key in shelter_fields.values():
                        flat_record[flat_key] = ""

                flattened_records.append(flat_record)

            # Get all field names from the flattened records
            fieldnames = list(dict.fromkeys(
                key for record in flattened_records for key in record
            ))

            with open(filename, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(flattened_records)

        else:
            return False, "File must be JSON or CSV."

        return True, None

    except (OSError, ValueError, TypeError, csv.Error):
        return False, "Unable to save records."


# Maintained by Htet Shine Aung (2604711)
# Add ONE processed record without deleting the existing records
def add_record(filename, record):

    # Load the existing records
    records, error = load_records(filename)

    # If the file does not exist, start with an empty list
    if error == "File not found.":
        records = []

    # If there is another error, stop
    elif error:
        return False, error

    records.append(record)

    # Save the updated list
    return save_records(filename, records)

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
# Check if the selected file is a valid JSON file
def validate_json_filename(filename):

    # Check if the file ends with .json
    if not filename.lower().endswith(".json"):
        return False, "Invalid file format. Please select a JSON file."

    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Check if the JSON contains a list
        if not isinstance(data, list):
            return False, "The JSON file must contain a list of records."

        return True, None

    except FileNotFoundError:
        return False, "JSON file not found."

    except json.JSONDecodeError:
        return False, "The JSON file is invalid."

    except (OSError, UnicodeDecodeError):
        return False, "Unable to read the JSON file."

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
                    "location": row.get("Address", "N/A"),
                    "description": row.get("Description", "")


                }

                shelters.append(shelter)

        return shelters, None

    except FileNotFoundError:
        return [], "CSV file not found."

    except (OSError, ValueError, TypeError, UnicodeDecodeError, csv.Error):
        return [], "Unable to load shelter data."


# Maintained by Htet Shine Aung (2604711)
# Update an existing client record using **kwargs
def update_record(filename, client_id, **kwargs):

    # Load existing records
    records, error = load_records(filename)

    if error:
        return False, error

    # Find the record to update
    for record in records:
        if str(record.get("client_id")) == str(client_id):

            # Update the record with new values
            record.update(kwargs)

            # Save the updated records
            return save_records(filename, records)

    return False, "Client record not found."

# Maintained by Htet Shine Aung (2604711)
# Remove a client record using client_id
def remove_record(filename, client_id):

    # Load existing records
    records, error = load_records(filename)

    if error:
        return False, error

    # Find and remove the client record
    for record in records:
        if str(record.get("client_id")) == str(client_id):
            records.remove(record)

            # Save the updated records
            return save_records(filename, records)

    return False, "Client record not found."

# Maintained by Htet Shine Aung (2604711)
# Modified by Ming Xuan (2604426)
# Filter processed records by the outcome
# Outcome mapping: True = Accepted, False = Rejected, None/Missing = Pending
def filter_records_by_outcome(records, outcome):
    filtered_records = []

    for record in records:
        record_outcome = record.get("outcome", None)

        # Match based on outcome type
        if outcome is None:
            # Filter for pending (missing/empty outcome)
            if record_outcome is None or record_outcome == "":
                filtered_records.append(record)
        elif outcome is True:
            # Filter for accepted
            if record_outcome is True:
                filtered_records.append(record)
        elif outcome is False:
            # Filter for rejected
            if record_outcome is False:
                filtered_records.append(record)

    return filtered_records

# Maintained by Htet Shine Aung (2604711)
# Get a client record by client_id
def get_clientid(filename, client_id):

    # Load existing records
    records, error = load_records(filename)

    if error:
        return None, error

    # Find the matching client record
    for record in records:
        if str(record.get("client_id")) == str(client_id):
            return record, None

    return None, "Client record not found."
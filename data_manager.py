import json
import csv

FILENAME = "case_records.json"

# Maintained by Htet Shine Aung (2604711)
def load_records():
    """Read all saved cases from the JSON file."""

    try:
        with open(FILENAME, "r", encoding="utf-8") as file:
            records = json.load(file)

        # The file should contain a list.
        if not isinstance(records, list):
            return [], "The file must contain a list of cases."

        # Each case should be a dictionary.
        for record in records:
            if not isinstance(record, dict):
                return [], "A case in the file has an invalid format."

        return records, None

    except FileNotFoundError:
        # On the first run, there is no file.
        return [], None
    
    except (json.JSONDecodeError, UnicodeDecodeError):
        return [], "The saved file is damaged or contains invalid JSON."
   
    except OSError:
        return [], "Unable to open the saved file."
    
# Maintained by Htet Shine Aung (2604711)
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

        return True,

    except FileNotFoundError:
        return False,

    except (OSError, csv.Error, UnicodeDecodeError): 
        return False,




   
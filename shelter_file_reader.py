import csv
import json
from pathlib import Path


class ShelterFileReader:
    REQUIRED_FIELDS = (
    "Category",
    "Shelter Name",
    "Current Occupants",
    "Maximum Capacity",
    "Requirements",
    "Description",
    "Address",
    "Contact"
)
    
    def validate_csv_filename(self, filename):
        if not isinstance(filename, (str, Path)):
            return False, "Invalid filename."

        if not str(filename).strip():
            return False, "Filename cannot be empty."

        if Path(filename).suffix.lower() != ".csv":
            return False, "File must be a CSV file."

        return True, None

    def validate_json_filename(self, filename):
        if not isinstance(filename, (str, Path)):
            return False, "Invalid filename."

        if not str(filename).strip():
            return False, "Filename cannot be empty."

        if Path(filename).suffix.lower() != ".json":
            return False, "File must be a JSON file."

        return True, None
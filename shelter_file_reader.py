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

    def load_shelters(self, filename):
        if not isinstance(filename, (str, Path)):
            return [], "Invalid filename."

        filename = str(filename)

        if not filename.strip():
            return [], "Filename cannot be empty."

        suffix = Path(filename).suffix.lower()

        if suffix not in (".csv", ".json"):
            return [], "Shelter file must be CSV or JSON."

        try:
            if suffix == ".csv":
                shelters = self._load_csv(filename)
            else:
                shelters = self._load_json(filename)

            return shelters, None

        except FileNotFoundError:
            return [], "Shelter file not found."

        except PermissionError:
            return [], "Permission denied when reading shelter file."

        except json.JSONDecodeError:
            return [], "Invalid shelter JSON format."

        except (ValueError, TypeError, csv.Error) as error:
            return [], f"Invalid shelter data: {error}"

        except (OSError, UnicodeError) as error:
            return [], f"Unable to read shelter file: {error}"

    def _load_csv(self, filename):
        """
        Read shelter information from CSV.
        """
        with open(
            filename,
            "r",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                raise ValueError("CSV file has no headers.")

            missing_fields = [
                field for field in self.REQUIRED_FIELDS
                if field not in reader.fieldnames
            ]

            if missing_fields:
                raise ValueError(
                    "Missing required columns: "
                    + ", ".join(missing_fields)
                )

            shelters = []

            for row_number, row in enumerate(reader, start=2):
                if None in row:
                    raise ValueError(
                        f"Unexpected extra columns at row {row_number}."
                    )

                shelter = self._normalise_shelter(
                    row,
                    row_number
                )

                shelters.append(shelter)

            return shelters

import csv
import json
from pathlib import Path

# Maintained by Htet Shine Aung (2604711)
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

    def __init__(self, filename):
        self._filename = filename

    # TODO: This method can be used for non-shelter files. Consider moving it to a general utility class
    # Maintained by Htet Shine Aung (2604711)
    @staticmethod
    def validate_csv_filename(filename):
        if not isinstance(filename, (str, Path)):
            return False, "Invalid filename."

        if not str(filename).strip():
            return False, "Filename cannot be empty."

        if Path(filename).suffix.lower() != ".csv":
            return False, "File must be a CSV file."

        return True, None

    # TODO: This method can be used for non-shelter files. Consider moving it to a general utility class
    # Maintained by Htet Shine Aung (2604711)
    @staticmethod
    def validate_json_filename(filename):
        if not isinstance(filename, (str, Path)):
            return False, "Invalid filename."

        if not str(filename).strip():
            return False, "Filename cannot be empty."

        if Path(filename).suffix.lower() != ".json":
            return False, "File must be a JSON file."

        return True, None

    # Maintained by Htet Shine Aung (2604711)
    def load_shelters(self):
        filename = self._filename
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
                shelters = self._load_csv()
            else:
                shelters = self._load_json()

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

    # Maintained by Htet Shine Aung (2604711)
    def _load_csv(self):
        """
        Read shelter information from CSV.
        """
        filename = self._filename
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

    # Maintained by Htet Shine Aung (2604711)
    def _load_json(self):
        filename = self._filename
        with open(
            filename,
            "r",
            encoding="utf-8-sig"
        ) as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError(
                "Shelter JSON must contain a list."
            )

        shelters = []

        for index, shelter in enumerate(data, start=1):
            if not isinstance(shelter, dict):
                raise ValueError(
                    f"Shelter {index} must be a dictionary."
                )

            shelters.append(
                self._normalise_shelter(shelter, index)
            )

        return shelters

    # Maintained by Htet Shine Aung (2604711)
    def _normalise_shelter(self, shelter, row_number):
        missing_fields = [
            field for field in self.REQUIRED_FIELDS
            if field not in shelter
        ]

        if missing_fields:
            raise ValueError(
                f"Row {row_number}: missing fields "
                + ", ".join(missing_fields)
            )

        result = dict(shelter)

        name = result.get("Shelter Name")

        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                f"Row {row_number}: shelter name is required."
            )

        result["Shelter Name"] = name.strip()

        for field in ("Current Occupants", "Maximum Capacity"):
            value = result.get(field)

            if isinstance(value, bool):
                raise ValueError(
                    f"Row {row_number}: {field} must be an integer."
                )

            try:
                number = int(value)
            except (ValueError, TypeError, OverflowError):
                raise ValueError(
                    f"Row {row_number}: {field} must be an integer."
                )

            if number < 0:
                raise ValueError(
                    f"Row {row_number}: {field} cannot be negative."
                )

            result[field] = number

        if (
            result["Current Occupants"]
            > result["Maximum Capacity"]
        ):
            raise ValueError(
                f"Row {row_number}: occupants exceed capacity."
            )

        # Normalize keys to lowercase format expected by other modules
        normalized = {
            "name": result["Shelter Name"],
            "category": result["Category"],
            "requirements": result["Requirements"],
            "capacity": result["Maximum Capacity"],
            "occupants": result["Current Occupants"],
            "description": result["Description"],
            "address": result["Address"],
            "contact": result["Contact"]
        }

        return normalized
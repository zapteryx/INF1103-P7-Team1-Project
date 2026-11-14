import json
import csv
from typing import Any

from .storage import Storage

# Maintained by Htet Shine Aung (2604711)
class FileStorage(Storage):
    def __init__(self, filename: str) -> None:
        self._filename = filename

    # Maintained by Htet Shine Aung (2604711)
    def load_records(self) -> tuple[list[dict[str, Any]], str | None]:
        filename = self._filename
        cases = []

        try:
            # Load JSON file
            if filename.lower().endswith(".json"):
                with open(filename, "r", encoding="utf-8") as file:
                    cases = json.load(file)

                # Make sure JSON contains a list
                if not isinstance(cases, list):
                    return [], "The JSON file must contain a list of cases."

                # Validate each case
                for case in cases:
                    if not isinstance(case, dict):
                        return [], "A case in the file has an invalid format."
            # Load CSV file
            elif filename.lower().endswith(".csv"):

                # Mapping for reconstructing accepted_shelter
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
                            "outcome": row.get("outcome", "")
                        }

                        # Handle approved field (convert string to bool)
                        approved_value = row.get("approved", "")
                        if approved_value:
                            if approved_value.lower() == "true":
                                case["approved"] = True
                            elif approved_value.lower() == "false":
                                case["approved"] = False
                            # If empty or invalid, don't set it (will default to True in .get("approved", True))

                        # Reconstruct nested shelter information
                        if row.get("accepted_shelter_name"):
                            accepted_shelter = {}

                            for flat_key, orig_key in shelter_fields.items():
                                value = row.get(flat_key, "")

                                if value:
                                    if orig_key in [
                                        "ai_suitability_score",
                                        "calculated_suitability_score",
                                        "ai_confidence_score"
                                    ]:
                                        accepted_shelter[orig_key] = float(value)

                                    elif orig_key in ["min_age", "max_age"]:
                                        accepted_shelter[orig_key] = int(value)

                                    elif orig_key == "dependents_allowed":
                                        accepted_shelter[orig_key] = (
                                            value.lower() == "true"
                                        )

                                    else:
                                        accepted_shelter[orig_key] = value

                            if accepted_shelter:
                                case["accepted_shelter"] = accepted_shelter

                        cases.append(case)

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
    def save_records(
    self, records: list[dict[str, Any]]
) -> tuple[bool, str | None]:
        
        filename = self._filename

        try:
            # Save JSON file
            if filename.lower().endswith(".json"):
                with open(filename, "w", encoding="utf-8") as file:
                    json.dump(records, file, indent=4)

            # Save CSV file
            elif filename.lower().endswith(".csv"):

                if not records:
                    return False, "Cannot save an empty CSV without headers."

                # Mapping for flattening shelter information
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

                flattened_records = []

                for record in records:
                    # Copy all fields except accepted_shelter
                    flat_record = {
                        k: v for k, v in record.items()
                        if k != "accepted_shelter"
                    }

                    accepted_shelter = record.get("accepted_shelter")

                    if accepted_shelter and isinstance(accepted_shelter, dict):

                        for orig_key, flat_key in shelter_fields.items():
                            value = accepted_shelter.get(orig_key, "")

                            if orig_key == "dependents_allowed":
                                flat_record[flat_key] = str(value)
                            else:
                                flat_record[flat_key] = value

                    else:
                        for flat_key in shelter_fields.values():
                            flat_record[flat_key] = ""

                    flattened_records.append(flat_record)

                # Collect all column names
                fieldnames = list(dict.fromkeys(
                    key
                    for record in flattened_records
                    for key in record
                ))

                with open(
                    filename,
                    "w",
                    newline="",
                    encoding="utf-8-sig"
                ) as file:

                    writer = csv.DictWriter(
                        file,
                        fieldnames=fieldnames
                    )

                    writer.writeheader()
                    writer.writerows(flattened_records)

            else:
                return False, "File must be JSON or CSV."

            return True, None

        except (OSError, ValueError, TypeError, csv.Error):
            return False, "Unable to save records."
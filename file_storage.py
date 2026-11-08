import json
import csv

from storage import Storage

# Maintained by Htet Shine Aung (2604711)
class FileStorage(Storage):
    def __init__(self, filename):
        self._filename = filename

    def load_records(self):
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
   
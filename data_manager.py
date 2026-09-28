import json

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
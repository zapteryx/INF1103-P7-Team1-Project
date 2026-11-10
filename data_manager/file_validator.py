from pathlib import Path


class FileValidator:

    @staticmethod
    def validate_csv_filename(
        filename: str | Path
    ) -> tuple[bool, str | None]:

        if not isinstance(filename, (str, Path)):
            return False, "Invalid filename."

        if not str(filename).strip():
            return False, "Filename cannot be empty."

        if Path(filename).suffix.lower() != ".csv":
            return False, "File must be a CSV file."

        return True, None

    @staticmethod
    def validate_json_filename(
        filename: str | Path
    ) -> tuple[bool, str | None]:

        if not isinstance(filename, (str, Path)):
            return False, "Invalid filename."

        if not str(filename).strip():
            return False, "Filename cannot be empty."

        if Path(filename).suffix.lower() != ".json":
            return False, "File must be a JSON file."

        return True, None

    @staticmethod
    def validate_db_filename(
        filename: str | Path
    ) -> tuple[bool, str | None]:

        if not isinstance(filename, (str, Path)):
            return False, "Invalid filename."

        if not str(filename).strip():
            return False, "Filename cannot be empty."

        if Path(filename).suffix.lower() != ".db":
            return False, "File must be a DB file."

        return True, None
from storage import Storage


class DataManager:
    def __init__(self, storage: Storage):
        if not isinstance(storage, Storage):
            raise TypeError(
                "storage must be an instance of Storage"
            )

        self._storage = storage

    def load_records(self):
        return self._storage.load_records()

    def save_records(self, records):
        if not isinstance(records, list):
            return False, "Records must be a list."
    
        if not all(isinstance(record, dict) for record in records):
            return False, "Every record must be a dictionary."
    
        return self._storage.save_records(records)

    def add_record(self, record):
        if not isinstance(record, dict):
            return False, "Record must be a dictionary."

        client_id = str(record.get("client_id", "")).strip()

        if not client_id:
            return False, "Client ID cannot be empty."

        records, error = self.load_records()

        if error == "File not found.":
            records = []
        elif error:
            return False, error

        for existing_record in records:
            existing_id = str(
                existing_record.get("client_id", "")
            ).strip()

            if existing_id == client_id:
                return False, "Client ID already exists."

        records.append(record)

        return self.save_records(records)

    def update_record(self, client_id, **kwargs):
        if not kwargs:
            return False, "No fields provided for update."

        records, error = self.load_records()

        if error:
            return False, error

        client_id = str(client_id).strip()

        for record in records:
            existing_id = str(
                record.get("client_id", "")
            ).strip()

            if existing_id == client_id:

                # Prevent changing the primary identifier
                if "client_id" in kwargs:
                    return False, "Client ID cannot be changed."

                record.update(kwargs)

                return self.save_records(records)

        return False, "Client record not found."
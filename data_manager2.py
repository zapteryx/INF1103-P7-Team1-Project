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
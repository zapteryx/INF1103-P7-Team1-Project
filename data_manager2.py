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

    
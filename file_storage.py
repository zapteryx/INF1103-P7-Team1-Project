import json
import csv

from storage import Storage


class FileStorage(Storage):
    def __init__(self, filename):
        self._filename = filename
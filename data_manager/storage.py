from abc import ABC, abstractmethod


# Maintained by Htet Shine Aung (2604711)
class Storage(ABC):

    @abstractmethod
    def load_records(self):
        pass

    @abstractmethod
    def save_records(self, records):
        pass
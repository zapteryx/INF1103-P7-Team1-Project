from abc import ABC, abstractmethod
from typing import Any


# Maintained by Htet Shine Aung (2604711)
class Storage(ABC):

    @abstractmethod
    def load_records(
    self
) -> tuple[list[dict[str, Any]], str | None]:
        pass

    @abstractmethod
    def save_records(
    self, records: list[dict[str, Any]]
) -> tuple[bool, str | None]:
        pass
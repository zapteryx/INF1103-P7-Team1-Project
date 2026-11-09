from abc import ABC, abstractmethod
import jsonschema
from .exceptions import DuplicateShelterError, InvalidAIOutputError, SchemaViolationError

# Maintained by Mei Qi (2605039)
# Template for checking the API's output
class OutputValidator(ABC):
    @property
    def name(self) -> str:
        return type(self).__name__

    @abstractmethod
    def validate(self, output: dict) -> None:
        pass

    def _fail(self, message: str, error_type=InvalidAIOutputError) -> None:
        raise error_type(f"{self.name}: {message}")

# Maintained by Mei Qi (2605039)
# Validates whether the API output followed the response schema
class SchemaValidator(OutputValidator):
    def __init__(self, schema: dict) -> None:
        self._schema = schema

    def validate(self, output: dict) -> None:
        try:
            jsonschema.validate(instance=output, schema=self._schema)
        except jsonschema.exceptions.ValidationError as e:
            self._fail(e.message, SchemaViolationError)

# Maintained by Mei Qi (2605039)
# Validates whether there are no duplicated shelter names in API output
class NoDuplicateSheltersValidator(OutputValidator):
    def validate(self, output: dict) -> None:
        names = [item["shelter_name"] for item in output["criteria_met"]]
        if len(names) != len(set(names)):
            self._fail("There are duplicated shelter names in the API output.", DuplicateShelterError)
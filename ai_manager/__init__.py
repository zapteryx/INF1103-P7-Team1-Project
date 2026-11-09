import json
import logging
from .clients import AIClient, GeminiClient, SampleResponseClient
from .exceptions import (
    AIError, AIServiceError, DuplicateShelterError, InvalidAIOutputError,
    MalformedJSONError, SchemaViolationError,
)
from .prompt_and_schema import PromptBuilder, ResponseSchema
from .validators import NoDuplicateSheltersValidator, OutputValidator, SchemaValidator

# Maintained by Mei Qi (2605039)
class AIManager:
    LOG_FILE = "ai_manager.log"
    
    def __init__(
        self,
        client: AIClient,
        fallback_client: AIClient | None = None,
        validators: list[OutputValidator] | None = None,
        prompt_builder: PromptBuilder | None = None,
        max_attempts: int = 3,
        logger: logging.Logger | None = None,
    ) -> None:
        self._client = client
        self._fallback_client = fallback_client
        self._max_attempts = max_attempts
        self._logger = logger or logging.getLogger("ai_manager")
        self._prompt_builder = prompt_builder or PromptBuilder()
        self._schema = ResponseSchema().get_schema()
        self._validators = validators if validators is not None else [
            SchemaValidator(self._schema),
            NoDuplicateSheltersValidator(),
        ]

    # Errors and success messages are written to a file, so that the messages doesn't clutter the terminal
    # Create and set log configurations based on file parameters, level of log messages, format of messages, style of format
    @staticmethod
    def configure_logging(filename: str = LOG_FILE) -> None:
        logging.basicConfig(
            filename=filename,
            encoding="utf-8",
            filemode="a",
            level=logging.INFO,
            format="{asctime} {levelname} {message}",
            style="{",
        )

    # Retrieves the API output if API call was successful, unless all attempts fail, it will try the fallback option
    def get_shelter_recommendation(self, client_info: dict, shelter_info: list[dict]) -> dict:
        prompt = self._prompt_builder.build(client_info, shelter_info)

        output = self._try_client(self._client, prompt, self._max_attempts)
        if output is not None:
            return output

        if self._fallback_client is not None:
            self._logger.warning(f"All {self._max_attempts} api attempts failed. Using fallback client.")
            output = self._try_client(self._fallback_client, prompt, 1)
            if output is not None:
                return output

        self._logger.error("All api attempts failed and no valid fallback was available.")
        raise AIServiceError("Unable to get a valid API response.")

    # Parses and validates the API output. If
    # Passes -> log success msg and returns dict. Fails -> logs error and retries. All attempts failed -> returns none
    def _try_client(self, client: AIClient, prompt: str, attempts: int) -> dict | None:
        for attempt in range(1, attempts + 1):
            try:
                output = self._parse(client.generate(prompt, self._schema))
                self._validate(output)
                self._logger.info("Api call was successful and output is valid.")
                self._logger.info(f"Api output: {output}")
                return output
            except InvalidAIOutputError as e:
                self._logger.error(f"Attempt {attempt}: api output is invalid: {e}")
            except Exception as e:  # api failures such as rate limits, timeouts, connection errors...
                self._logger.error(f"Attempt {attempt}: api call failed: {e}")
        return None

    # Converts API output to dictionary
    @staticmethod
    def _parse(raw: str) -> dict:
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError) as e:
            raise MalformedJSONError(f"api output is not valid JSON: {e}") from e

    # Runs all validators on the API output
    def _validate(self, output: dict) -> None:
        for validator in self._validators:  # polymorphism: no type checks needed
            validator.validate(output)

__all__ = [
    "AIManager",
    "AIClient",
    "GeminiClient",
    "SampleResponseClient",
    "AIError",
    "AIServiceError",
    "DuplicateShelterError",
    "InvalidAIOutputError",
    "MalformedJSONError",
    "SchemaViolationError",
    "PromptBuilder",
    "ResponseSchema",
    "NoDuplicateSheltersValidator",
    "OutputValidator",
    "SchemaValidator",
]
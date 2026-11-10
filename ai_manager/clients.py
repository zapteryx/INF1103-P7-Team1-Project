import json
from dotenv import load_dotenv
from google import genai
from abc import ABC, abstractmethod
from .exceptions import InvalidAIOutputError

# Maintained by Mei Qi (2605039)
class AIClient(ABC):
    @abstractmethod
    def generate(self, prompt: str, schema: dict) -> str:
        pass

# Maintained by Mei Qi (2605039)
# Gets a Gemini client and calls the API, then returns the API output
class GeminiClient(AIClient):
    def __init__(self, model: str = "gemini-3.1-flash-lite") -> None:
        self._model = model
        self._client: genai.Client | None = None

    def _get_client(self) -> genai.Client:
        if self._client is None:
            load_dotenv()  # reads the .env file (which contains the API key)
            self._client = genai.Client()
        return self._client

    def generate(self, prompt: str, schema: dict) -> str:
        interaction = self._get_client().interactions.create(
            model=self._model,
            input=prompt,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": schema,
            },
        )
        return interaction.output_text

# Maintained by Mei Qi (2605039)
# Sample API response used instead for offline demos and testing
class SampleResponseClient(AIClient):
    def __init__(self, path: str = "sample_api_response.json") -> None:
        self._path = path

    def generate(self, prompt: str, schema: dict) -> str:
        with open(self._path, encoding="utf-8") as file:
            data = json.load(file)
        for step in data["steps"]:
            if step["type"] == "model_output":
                return step["content"][0]["text"]
        raise InvalidAIOutputError("No model_output step is found in the sample response file.")
import io_manager
import json
import jsonschema
import logging
from jsonschema import validate
from dotenv import load_dotenv
from google import genai

# Maintained by Mei Qi (2605039)
# Reads the .env file (which contains the API key)
load_dotenv()

# Load the shelter data using functions from io_manager
file_path = io_manager.get_shelter_filename()
shelters = io_manager.load_shelters_from_csv(file_path)

# Convert each shelter dict to text and join them
shelter_info = "\n".join(io_manager.format_shelter(s) for s in shelters)

# Retrieve the client info using functions from io_manager
client_info = io_manager.collect_intake_input()

# Errors are written to a file, so that the messages doesn't clutter the terminal
# Create and set log configurations based on file parameters, level of log messages, format of messages, style of format
logging.basicConfig(
    filename="ai_manager.log", 
    encoding="utf-8", 
    filemode="a", 
    level=logging.INFO, 
    format="{asctime} {levelname} {message}", 
    style="{"
)

# Maintained by Mei Qi (2605039)
def get_shelter_recomendation(client_info: str, shelter_info: str) -> dict | None:
    # Create a schema for the output after calling the api
    response_schema = {
        "type": "object",
        "properties": {
            "urgency_level": {
                "type": "integer",
                "description": "Urgency level of case"
            },
            "criterias_met": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "shelter_name": {"type": "string"},
                        "criteria": {"type": "string"},
                        "met": {"type": "boolean"}
                    }
                },
                "description": "List of criterias the shelter met based on the case"
            }
        },
        "required": ["urgency_level", "criterias_met"]
    }

    # Create a prompt using the shelter and client info
    prompt = f"""Based on the client and shelter information shown, determine the urgency level of the case 
    (from 1-5, where 5 is the most urgent and 1 is the least urgent), give a structured JSON dictionary of criterias 
    that the shelter meets for the case, and provide a recommended shelter for the client.\n 
    Client info:\n {client_info} \nShelter info:\n {shelter_info}"""

    try:
        client = genai.Client()

        # Call the api to give a prompt based on the parameters shown below
        interaction = client.interactions.create(
            model="gemini-3.1-flash-lite",
            input=prompt,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": response_schema
            },
        )

        output = json.loads(interaction.output_text)

        # Validates the api output based on response schema
        validate(instance=output, schema=response_schema)
        logging.info("Api call was successful and output is valid.")

        # Converts from Python dictionary to JSON text
        print(json.dumps(output, indent=2))

    # Logs all api failures and invalid api output into a file, and uses the sample api response instead of calling api again
    except jsonschema.exceptions.ValidationError as e:
        logging.error("Api call is invalid: {e.message}")

        # Opens the sample api response file and loops through the list called steps to retrieve the output text
        with open("sample_api_response.json", encoding="utf-8") as file:
            data = json.load(file)
        for step in data["steps"]:
            if step["type"] == "model_output":
                return json.loads(step["content"][0]["text"])
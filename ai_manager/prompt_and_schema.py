import json

# Maintained by Mei Qi (2605039)
# Create a schema for the output to follow after calling the API
class ResponseSchema:
    def __init__(self) -> None:
        self._schema = {
            "type": "object",
            "properties": {
                "urgency_level": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 5,
                    "description": "Urgency level of case (1 = least urgent, 5 = most urgent)",
                },
                "criteria_met": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "shelter_name": {
                                "type": "string",
                                "description": "Must match the shelter name exactly as shown in the shelter info",
                            },
                            "criteria": {
                                "type": "string",
                                "description": "The requirement of the shelter that the client met",
                            },
                            "gender_restriction": {
                                "type": "string",
                                "enum": ["Male", "Female", "Any"],
                                "description": "Use 'Any' if the shelter has no gender restriction",
                            },
                            "dependents_allowed": {
                                "type": "boolean"
                            },
                            "min_age": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 120,
                                "description": "The minimum age of the client allowed in the shelter. "
                                               "Use 0 if the shelter does not state a minimum age.",
                            },
                            "max_age": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 120,
                                "description": "The maximum age of the client allowed in the shelter. "
                                               "Use 120 if the shelter does not state a maximum age.",
                            },
                            "ai_confidence_score": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                                "description": "AI's confidence in this match from 0.0 to 1.0, where 0.0 is not "
                                               "confident and 1.0 is fully confident, and must be rounded to "
                                               "2 decimal place (e.g. 0.80)",
                            },
                            "suitability_score": {
                                "type": "number",
                                "minimum": 1,
                                "maximum": 100,
                                "description": "How well the shelter suits this client from 1.0 to 100.0, where 1.0 "
                                               "is least suitable and 100.0 is most suitable, and must be rounded "
                                               "to 1 decimal place (e.g. 87.5)",
                            },
                        },
                        "required": [
                            "shelter_name",
                            "criteria",
                            "gender_restriction",
                            "dependents_allowed",
                            "min_age", "max_age",
                            "ai_confidence_score",
                            "suitability_score",
                        ],
                    },
                    "description": "Include only the criteria that are met. "
                                   "Exclude any shelter or criterion that is not met.",
                },
            },
            "required": ["urgency_level", "criteria_met"],
        }

    def get_schema(self) -> dict:
        return self._schema

# Maintained by Mei Qi (2605039)
# Create a prompt using the shelter and client info
class PromptBuilder:
    def build(self, client_info: dict, shelter_info: list[dict]) -> str:
        client_text = json.dumps(client_info, indent=2, default=str)
        shelter_text = json.dumps(shelter_info, indent=2, default=str)
        return (
            f"""Based on the client and shelter information shown, determine the urgency level of the case
            (from 1-5, where 5 is the most urgent and 1 is the least urgent). Give a structured JSON
            dictionary that lists only the shelters and criteria that the client meets. Do not include any
            shelter or criterion that is not met. In the output each shelter must be shown at most once.
            Client info: {client_text}
            Shelter info: {shelter_text}"""
        )
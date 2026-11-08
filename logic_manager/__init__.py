from .recommendation_validator import RecommendationValidator
from .shelter_evaluator import Evaluator, GenderEvaluator, CareTypeEvaluator

class LogicManager:

    def __init__(self):
        self._validator = RecommendationValidator()
        self._evaluators = [GenderEvaluator(), CareTypeEvaluator()]

    @property
    def validator(self):
        """Getter for validator using @property as taught in Week 9."""
        return self._validator

    def validate_ai_recommendation(self, ai_recommendation: dict, shelter_csv: list[dict]):
        return self._validator.validate_ai_recommendation(ai_recommendation, shelter_csv)

    def calculate_suitability_score(self, shelter_csv: list[dict], client_data: dict, ai_recommendation: dict):
        client_gender = client_data.get("gender", "")
        client_dependent = int(client_data.get("dependents", 0))

        flag, flag_reasons, accepted_shelter_names = self.validate_ai_recommendation(
            ai_recommendation, shelter_csv
        )

        shelter_lookup = {row["name"]: row for row in shelter_csv if "name" in row}
        result = []

        for ai_shelter in ai_recommendation.get("criteria_met", []):
            shelter_name = ai_shelter.get("shelter_name")

            if shelter_name not in accepted_shelter_names:
                result.append({"name": shelter_name, "score": -999})
                continue

            shelter_score = (ai_shelter.get("suitability_score", 0) * 0.4) + (ai_shelter.get("ai_confidence_score", 0) * 30)

            shelter_exists = shelter_lookup.get(shelter_name)
            if shelter_exists:
                available_capacity = int(shelter_exists.get("capacity", 0)) - int(shelter_exists.get("occupants", 0))
                if available_capacity < (client_dependent + 1):
                    shelter_score -= 60

                ai_gender_restriction = ai_shelter.get("gender_restriction")
                if ai_gender_restriction and ai_gender_restriction.lower() not in (client_gender.lower(), "any"):
                    flag_reasons.append(
                        f"REJECT: {client_gender} client is mismatched for {shelter_name} ({ai_gender_restriction}-only)."
                    )
                    result.append({"name": shelter_name, "score": -999})
                    continue

                shelter_description = shelter_exists.get("description", "")
                rejected = False

                for i in self._evaluators:
                    delta, reason = i.evaluate(shelter_description, client_data)
                    if delta <= -900:
                        result.append({"name": shelter_name, "score": -999})
                        if reason:
                            flag_reasons.append(reason)
                        rejected = True
                        break
                    shelter_score += delta

                if rejected:
                    continue

                result.append({"name": shelter_name, "score": shelter_score})
            else:
                result.append({"name": shelter_name, "score": -999})

        ranked_results = sorted(result, key=lambda x: x["score"], reverse=True)

        for shelter in ai_recommendation.get("criteria_met", []):
            if ranked_results and shelter["shelter_name"] == ranked_results[0]["name"] and ranked_results[0]["score"] > -500:
                return {
                    "rank": "1",
                    "shelter_name": shelter["shelter_name"],
                    "ai_suitability_score": shelter["suitability_score"],
                    "calculated_suitability_score": ranked_results[0]["score"],
                    "ai_confidence_score": shelter["ai_confidence_score"],
                    "min_age": shelter["min_age"],
                    "max_age": shelter["max_age"],
                    "gender_restriction": shelter["gender_restriction"],
                    "dependents_allowed": shelter["dependents_allowed"],
                }

        return None

__all__ = [
    "LogicManager",
    "RecommendationValidator",
    "Evaluator",
    "GenderEvaluator",
    "CareTypeEvaluator",
]

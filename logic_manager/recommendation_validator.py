class RecommendationValidator:
    """Validator class implementing Encapsulation (Week 8)."""

    def check_urgency_level(self, ai_recommendation: dict):
        urgency_level = ai_recommendation.get("urgency_level")
        if urgency_level is None or not (1 <= urgency_level <= 5):
            return ["FLAG: Urgency level is out of range (1-5)."]
        return []

    def check_shelter_names(self, criteria_met: list[dict], shelter_csv: list[dict]):
        ai_shelter_names = {item["shelter_name"] for item in criteria_met}
        shelter_count = 0
        target_count = len(criteria_met)
        accepted_shelter_names = []
        reasons = []

        for row in shelter_csv:
            if row.get("name") in ai_shelter_names:
                shelter_count += 1
                accepted_shelter_names.append(row["name"])

        flagged = shelter_count < target_count
        if flagged:
            for item in criteria_met:
                if item["shelter_name"] not in accepted_shelter_names:
                    reasons.append(f"FLAG: {item['shelter_name']} does not exist.")

        return flagged, reasons, accepted_shelter_names

    def check_score_ranges(self, shelter: dict):
        reasons = []
        if not (0 <= shelter.get("ai_confidence_score", 0) <= 1):
            reasons.append(f"FLAG: AI confidence score for {shelter['shelter_name']} is out of range (0-1).")
        if not (0 <= shelter.get("suitability_score", 0) <= 100):
            reasons.append(f"FLAG: AI suitability score for {shelter['shelter_name']} is out of range (0-100).")
        return reasons

    def check_age_range(self, shelter: dict):
        min_age = shelter.get("min_age", 0)
        max_age = shelter.get("max_age", 120)
        if min_age > max_age or min_age < 0 or min_age > 100 or max_age < 1 or max_age > 120:
            return [f"FLAG: AI age range for {shelter['shelter_name']} is out of bounds."]
        return []

    def check_gender_restriction(self, shelter: dict):
        gender_restriction = shelter.get("gender_restriction")
        if gender_restriction is None or gender_restriction.lower() not in ["male", "female", "any"]:
            return [f"FLAG: AI gender restriction for {shelter['shelter_name']} is invalid."]
        return []

    def validate_shelter_entry(self, shelter: dict):
        return (
            self.check_score_ranges(shelter)
            + self.check_age_range(shelter)
            + self.check_gender_restriction(shelter)
        )

    def validate_ai_recommendation(self, ai_recommendation: dict, shelter_csv: list[dict]):
        flag_reasons = []
        flag = "ACCEPT"

        try:
            urgency_reasons = self.check_urgency_level(ai_recommendation)
            if urgency_reasons:
                flag_reasons.extend(urgency_reasons)
                flag = "FLAG"

            criteria_met = ai_recommendation.get("criteria_met", [])
            name_flagged, name_reasons, accepted_shelter_names = self.check_shelter_names(criteria_met, shelter_csv)
            flag_reasons.extend(name_reasons)
            if name_flagged:
                flag = "FLAG"

            for shelter in criteria_met:
                reasons = self.validate_shelter_entry(shelter)
                flag_reasons.extend(reasons)
                if reasons and shelter.get("shelter_name") in accepted_shelter_names:
                    accepted_shelter_names.remove(shelter.get("shelter_name"))
                    flag = "FLAG"

            return flag, flag_reasons, accepted_shelter_names

        except Exception as e:
            flag = "FLAG"
            flag_reasons.append(f"FLAG: Error validating AI recommendation: {str(e)}")
            return flag, flag_reasons, []
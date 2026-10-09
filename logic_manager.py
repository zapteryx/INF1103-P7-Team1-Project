import json
import csv

CSV_FILENAME = "singapore_shelters_directory.csv"


def validate_json(json_string):
    try:
        json.loads(json_string)
        return True
    except ValueError as e:
        return False


def validate_ai_recommendation(ai_recommendation):
    flag_reasons = []
    flag = "ACCEPT"
    try:
        # data = json.loads(json_string)
        # validate urgency level within range 1-5
        if not 0 < ai_recommendation.get("urgency_level") < 6:
            flag_reasons.append("FLAG: Urgency level is out of range (1-5).")
            flag = "FLAG"

        # validate shelter names against CSV file
        criteria_met = ai_recommendation.get("criteria_met", [])
        ai_shelter_names = {item["shelter_name"] for item in criteria_met}
        shelter_count = 0
        target_count = len(criteria_met)
        accepted_shelter_names = []
        with open(CSV_FILENAME, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["Shelter Name"] in ai_shelter_names:
                    shelter_count += 1
                    accepted_shelter_names.append(row["Shelter Name"])
        # if there is an incorrect shelter name, the name will be added to flag_reasons
        if shelter_count < target_count:
            for i in criteria_met:
                if i["shelter_name"] not in accepted_shelter_names:
                    flag_reason = f"FLAG: {i['shelter_name']} does not exist."
                    flag_reasons.append(flag_reason)
            flag = "FLAG"

        # validate ai_confidence_score and suitability_score within range
        for i in criteria_met:
            individual_flag = "ACCEPT"
            if not 0 <= i.get("ai_confidence_score", 0) <= 1:
                flag_reasons.append(
                    f"FLAG: AI confidence score for {i['shelter_name']} is out of range (0-1)."
                )
                individual_flag = "FLAG"
            if not 0 <= i.get("suitability_score", 0) <= 100:
                flag_reasons.append(
                    f"FLAG: AI suitability score for {i['shelter_name']} is out of range (0-100)."
                )
                individual_flag = "FLAG"
            # sanitize and validate min_age and max_age
            min_age = i.get("min_age", 0)
            max_age = i.get("max_age", 120)
            if  min_age > max_age or min_age < 0 or min_age > 100 or max_age < 1 or max_age > 120:
                flag_reasons.append(f"FLAG: AI age range for {i['shelter_name']} is out of bounds.")
                individual_flag = "FLAG"
            # sanitize and validate gender_restriction
            if i.get("gender_restriction") not in ["Male", "Female", "any"]:
                flag_reasons.append(f"FLAG: AI gender restriction for {i['shelter_name']} is invalid.")
                individual_flag = "FLAG"

            #if the individual_flag is "FLAG", remove the shelter name from accepted_shelter_names
            if i.get("shelter_name") in accepted_shelter_names and individual_flag == "FLAG":
                accepted_shelter_names.remove(i.get("shelter_name"))
                flag = individual_flag





        return flag, flag_reasons, accepted_shelter_names

    except Exception as e:
        flag = "FLAG"
        flag_reasons.append("FLAG: Unexpected error occurred.")


def calculate_suitability_score(client_data, ai_recommendation):

    flag, flag_reasons, accepted_shelter_names = validate_ai_recommendation(ai_recommendation)
    score = 0
    result = []
    for shelter in ai_recommendation["criteria_met"]:
        if shelter["shelter_name"] not in accepted_shelter_names:
            rank = "0"
        # ai score is weighted at 30% of the total score, while the remaining 70% is based on other factors
        shelter_score = shelter["suitability_score"] * 0.3  # Weighting factor for AI recommendation

        with open(CSV_FILENAME, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            shelter_exists = next((row for row in reader if row.get("Shelter Name") == shelter["shelter_name"]), None)

        if shelter_exists:
            available_capacity = int(shelter_exists.get("Maximum Capacity", 0)) - int(shelter_exists.get("Current Occupants", 0))
            if available_capacity <= 0 :
                shelter_score -= 20  # Penalize for no available capacity
        result.append({"name": shelter["shelter_name"], "score": shelter_score})
    ranked_results = sorted(result, key=lambda x: x["score"], reverse=True)
    for shelter in ai_recommendation["criteria_met"]:
        if shelter["shelter_name"] == ranked_results[0]["name"]:
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






    # # Check age requirement
    # if client_data["age"] < ai_recommendation["min_age"]:
    #     score -= 10
    #     reasons.append(f"Client age {client_data['age']} is below minimum age {ai_recommendation['min_age']}.")
    # elif client_data["age"] > ai_recommendation["max_age"]:
    #     score -= 10
    #     reasons.append(f"Client age {client_data['age']} is above maximum age {ai_recommendation['max_age']}.")

    # # Check gender requirement
    # if ai_recommendation["gender_restriction"] and client_data["gender"] != ai_recommendation["gender_restriction"]:
    #     score -= 10
    #     reasons.append(f"Client gender {client_data['gender']} does not match AI recommendation gender restriction {ai_recommendation['gender_restriction']}.")

    # # Check family requirement
    # if ai_recommendation["family_only"] and client_data["dependents"] == 0:
    #     score -= 10
    #     reasons.append("Client has no dependents but shelter requires families.")

    # # Additional criteria checks can be added here

    # return score, reasons


def json_to_dict(json_string):
    if x == 3:
        x = 4

# with open("stuff.json", "r") as f:
#     stuff = json.load(f)
# validate_ai_recommendation(json.dumps(stuff))
# calculate_suitability_score({}, stuff)  # Assuming you want to calculate suitability for the same data


# when do we flag an ai response, when only 1 shelter recommended hallucinates?
# Decide an outcome: flag, score, route, accept, or reject
# compare user input age to the requirement
# Has 0 dependents but shelter requires Families (-999.0) (Disqualified)

# NEED GENDER, MIN AGE, MAX AGE, FAMILY ONLY, PETS ALLOWED

# if rules["gender_restriction"] and client_gender and client_gender != rules["gender_restriction"]:
# return -999.0, [f"REJECT: Gender mismatch for {shelter_name} (Requires {rules['gender_restriction']})."]

# if rules["family_only"] and client_dependents == 0:
# return -999.0, [f"REJECT: {shelter_name} requires dependents/families."]

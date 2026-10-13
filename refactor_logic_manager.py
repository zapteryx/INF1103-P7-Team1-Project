import json


def validate_json(json_string):
    try:
        json.loads(json_string)
        return True
    except ValueError as e:
        return False


def check_urgency_level(ai_recommendation):
    if not 0 < ai_recommendation.get("urgency_level") < 6:
        return ["FLAG: Urgency level is out of range (1-5)."]
    return []


def check_shelter_names(criteria_met, shelter_csv):
    ai_shelter_names = {item["shelter_name"] for item in criteria_met}
    shelter_count = 0
    target_count = len(criteria_met)
    accepted_shelter_names = []
    reasons = []
    for row in shelter_csv:
        if row["name"] in ai_shelter_names:
            shelter_count += 1
            accepted_shelter_names.append(row["name"])
    flagged = shelter_count < target_count
    if flagged:
        for i in criteria_met:
            if i["shelter_name"] not in accepted_shelter_names:
                reasons.append(f"FLAG: {i['shelter_name']} does not exist.")
    return flagged, reasons, accepted_shelter_names


def check_score_ranges(shelter):
    reasons = []
    if not 0 <= shelter.get("ai_confidence_score", 0) <= 1:
        reasons.append(f"FLAG: AI confidence score for {shelter['shelter_name']} is out of range (0-1).")
    if not 0 <= shelter.get("suitability_score", 0) <= 100:
        reasons.append(f"FLAG: AI suitability score for {shelter['shelter_name']} is out of range (0-100).")
    return reasons


def check_age_range(shelter):
    min_age = shelter.get("min_age", 0)
    max_age = shelter.get("max_age", 120)
    if min_age > max_age or min_age < 0 or min_age > 100 or max_age < 1 or max_age > 120:
        return [f"FLAG: AI age range for {shelter['shelter_name']} is out of bounds."]
    return []


def check_gender_restriction(shelter):
    if shelter.get("gender_restriction") not in ["male", "female", "any"]:
        return [f"FLAG: AI gender restriction for {shelter['shelter_name']} is invalid."]
    return []


def validate_shelter_entry(shelter):
    return (check_score_ranges(shelter)
            + check_age_range(shelter)
            + check_gender_restriction(shelter)
    )


def validate_ai_recommendation(ai_recommendation, shelter_csv):
    flag_reasons = []
    flag = "ACCEPT"
    try:
        # data = json.loads(json_string)
        # validate urgency level within range 1-5
        urgency_reasons = check_urgency_level(ai_recommendation)
        if urgency_reasons:
            flag_reasons += urgency_reasons
            flag = "FLAG"

        # validate shelter names against CSV file
        criteria_met = ai_recommendation.get("criteria_met", [])
        name_flagged, name_reasons, accepted_shelter_names = check_shelter_names(criteria_met, shelter_csv)
        flag_reasons += name_reasons
        if name_flagged:
            flag = "FLAG"

        # validate each shelter's scores, age range and gender restriction
        for i in criteria_met:
            reasons = validate_shelter_entry(i)
            flag_reasons += reasons
            if reasons and i.get("shelter_name") in accepted_shelter_names:
                accepted_shelter_names.remove(i.get("shelter_name"))
                flag = "FLAG"

        return flag, flag_reasons, accepted_shelter_names

    except Exception as e:
        flag = "FLAG"
        flag_reasons.append(f"FLAG: Error validating AI recommendation: {str(e)}")
        return flag, flag_reasons, []


def calculate_suitability_score(client_data, ai_recommendation):
    client_age = 0
    client_gender = "Male"
    client_dependent = 1
    
    
    flag, flag_reasons, accepted_shelter_names = validate_ai_recommendation(ai_recommendation)
    score = 0
    result = []
    with open(CSV_FILENAME, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        
    for shelter in ai_recommendation["criteria_met"]:
        if shelter["shelter_name"] not in accepted_shelter_names:
            result.append({"name": shelter["shelter_name"], "score": -999})
            continue # Skip shelters that are not accepted
        
        # ai score is weighted at 30% of the total score, while the remaining 70% is based on other factors
        shelter_score = shelter["suitability_score"] * 0.3  # Weighting factor for AI recommendation

        
        shelter_exists = next((row for row in reader if row.get("Shelter Name") == shelter["shelter_name"]), None)

        if shelter_exists:
            available_capacity = int(shelter_exists.get("Maximum Capacity", 0)) - int(shelter_exists.get("Current Occupants", 0))
            if available_capacity <= 0 :
                shelter_score -= 30  # Penalize for no available capacity
                
        #checks if client gender aligns with ai gender restriction        
        if shelter["gender_restriction"] not in (client_gender, "Any"):
            flag_reasons.append(f"REJECT: {client_gender} client is mismatched for {shelter['shelter_name']} ({shelter['gender_restriction']}-only).")
            result.append({"name": shelter["shelter_name"], "score": -999})
            continue

        #women, senior, adult, female, male, girls, children
            
            
        result.append({"name": shelter["shelter_name"], "score": shelter_score})
    ranked_results = sorted(result, key=lambda x: x["score"], reverse=True)
    for shelter in ai_recommendation["criteria_met"]:
        if shelter["shelter_name"] == ranked_results[0]["name"] and ranked_results[0]["score"] > -500:
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





#IMPORTANT LOOK HERE!!!!!!!!!!!!!!!!!!!!!!!!!!

# with open("newaireco.json", "r") as f:
#     stuff = json.load(f)
# validate_ai_recommendation(json.dumps(stuff))





# when do we flag an ai response, when only 1 shelter recommended hallucinates?
# Decide an outcome: flag, score, route, accept, or reject
# compare user input age to the requirement
# Has 0 dependents but shelter requires Families (-999.0) (Disqualified)

# NEED GENDER, MIN AGE, MAX AGE, FAMILY ONLY, PETS ALLOWED

# if rules["gender_restriction"] and client_gender and client_gender != rules["gender_restriction"]:
# return -999.0, [f"REJECT: Gender mismatch for {shelter_name} (Requires {rules['gender_restriction']})."]

# if rules["family_only"] and client_dependents == 0:
# return -999.0, [f"REJECT: {shelter_name} requires dependents/families."]

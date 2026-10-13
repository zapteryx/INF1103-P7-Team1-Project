import json
import re


LONG_TERM_KEYWORDS = ["long term", "long-term", "longterm", "supportive housing"]
SHORT_TERM_KEYWORDS = ["short term", "short-term", "emergency", "crisis", "transitional"]

SPECIAL_NEEDS_KEYWORDS = ["disability", "wheelchair", "impairment", "assisted living"]

ONLY_WOMEN_KEYWORDS = ["women", "female", "women only", "mothers"]
ONLY_MEN_KEYWORDS = ["men", "male", "fathers"]

BONUS_POINTS_MATCH = +40       # Reward for explicit alignment
PENALTY_POINTS_MISMATCH = -50  # Penalty for explicit conflict


    
def has_keyword(sentence, keywords: list[str]):
    if not sentence or not keywords:
        return False
    sentence_clean = str(sentence).lower()
    patterns = [r"\b" + re.escape(str(i).lower()) + r"\b" for i in keywords]
    return bool(re.search("|".join(patterns), sentence_clean))


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


def validate_ai_recommendation(ai_recommendation, shelter_csv):
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
        # with open(SHELTER_CSV_FILENAME, mode="r", encoding="utf-8") as file:
        #     reader = csv.DictReader(file)
        for i in shelter_csv:
            if i["name"] in ai_shelter_names:
                shelter_count += 1
                accepted_shelter_names.append(i["name"])
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
            if i.get("gender_restriction").lower() not in ["male", "female", "any"]:
                flag_reasons.append(f"FLAG: AI gender restriction for {i['shelter_name']} is invalid.")
                individual_flag = "FLAG"

            #if the individual_flag is "FLAG", remove the shelter name from accepted_shelter_names
            if i.get("shelter_name") in accepted_shelter_names and individual_flag == "FLAG":
                accepted_shelter_names.remove(i.get("shelter_name"))
                flag = individual_flag

        return flag, flag_reasons, accepted_shelter_names

    except Exception as e:
        flag = "FLAG"
        flag_reasons.append(f"FLAG: Error validating AI recommendation: {str(e)}")
        return flag, flag_reasons, []


def calculate_suitability_score(shelter_csv, client_data, ai_recommendation):
    client_age = int(client_data["age"])
    client_gender = client_data["gender"]
    client_dependent = int(client_data["dependents"])
    client_care_type = client_data["care_type"]
    is_special_needs = client_data["special_needs"]
    
    
    flag, flag_reasons, accepted_shelter_names = validate_ai_recommendation(ai_recommendation, shelter_csv)
    score = 0
    result = []
    # with open(SHELTER_CSV_FILENAME, mode="r", encoding="utf-8") as file:
    #     reader = list(csv.DictReader(file))
    
    #create a dict so i can lookup a name without for loop
    shelter_lookup = {}
    for row in shelter_csv:
        if "name" in row:
            shelter_name = row["name"]
            shelter_lookup[shelter_name] = row
        
    for ai_shelter in ai_recommendation["criteria_met"]:
        if ai_shelter["shelter_name"] not in accepted_shelter_names:
            result.append({"name": ai_shelter["shelter_name"], "score": -999})
            continue # Skip shelters that are not accepted
        
        # ai score is weighted at 30% of the total score, while the remaining 70% is based on other factors
        shelter_score = ai_shelter["suitability_score"] * 0.4  # Weighting factor for AI recommendation
        shelter_score += ai_shelter["ai_confidence_score"] * 30

        
        shelter_exists = shelter_lookup.get(ai_shelter["shelter_name"])
        if shelter_exists:
            available_capacity = int(shelter_exists.get("capacity", 0)) - int(shelter_exists.get("occupants", 0))
            if available_capacity < (client_dependent + 1):
                shelter_score -= 60  # Penalize for no available capacity



            #checks if client gender aligns with ai gender restriction
            if ai_shelter["gender_restriction"].lower() not in (client_gender.lower(), "any"):
                flag_reasons.append(f"REJECT: {client_gender} client is mismatched for {ai_shelter['shelter_name']} ({ai_shelter['gender_restriction']}-only).")
                result.append({"name": ai_shelter["shelter_name"], "score": -999})
                continue


            shelter_description = shelter_exists.get("description") or ""
            #checks the csv data for keywords relating gender and comparing it to the client
            client_gender_clean = client_gender.lower().strip()
            if client_gender_clean == "female":
                # 1. MISMATCH CHECK: Is the shelter strictly for men/males?
                if has_keyword(shelter_description, ONLY_MEN_KEYWORDS):
                    result.append({"name": ai_shelter["shelter_name"], "score": -999})
                    flag_reasons.append(f"REJECT: {client_gender} client is mismatched for {ai_shelter['shelter_name']} ({ai_shelter['gender_restriction']}-only).")
                    continue
                elif has_keyword(shelter_description, ONLY_WOMEN_KEYWORDS):
                    shelter_score += BONUS_POINTS_MATCH
                    
            elif client_gender_clean == "male":
                if has_keyword(shelter_description, ONLY_WOMEN_KEYWORDS):
                    result.append({"name": ai_shelter["shelter_name"], "score": -999})
                    flag_reasons.append(f"REJECT: {client_gender} client is mismatched for {ai_shelter['shelter_name']} ({ai_shelter['gender_restriction']}-only).")
                    continue
                elif has_keyword(shelter_description, ONLY_MEN_KEYWORDS):
                    shelter_score += BONUS_POINTS_MATCH
                
            
            
            #check from shelter csv for any long-term keywords, means shelter offers long-term care
            if "long term" == client_care_type.lower():
                if has_keyword(shelter_description, LONG_TERM_KEYWORDS):
                    shelter_score += BONUS_POINTS_MATCH
            
                elif has_keyword(shelter_description, SHORT_TERM_KEYWORDS):
                    shelter_score += PENALTY_POINTS_MISMATCH

            #check from shelter csv for any short-term keywords, means shelter offers short-term care
            elif "short term" == client_care_type.lower():
                if has_keyword(shelter_description, SHORT_TERM_KEYWORDS):
                    shelter_score += BONUS_POINTS_MATCH
            
                elif has_keyword(shelter_description, LONG_TERM_KEYWORDS):
                    shelter_score += PENALTY_POINTS_MISMATCH
                    
                    
            
                
            #women, senior, adult, female, male, girls, children
            
            
            result.append({"name": ai_shelter["shelter_name"], "score": shelter_score})
        else:
            result.append({"name": ai_shelter["shelter_name"], "score": -999})
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

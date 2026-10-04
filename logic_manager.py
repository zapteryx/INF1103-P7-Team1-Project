import json
import csv

CSV_FILENAME = "singapore_shelters_directory.csv"


def validate_json(json_string):
    try:
        json.loads(json_string)
        return True
    except ValueError as e:
        return False


def validate_ai_recommendation(json_string):
    flag_reasons = []
    flag = "ACCEPT"
    try:
        # data = json.loads(json_string)
        # validate urgency level within range 1-5
        if not 0 < json_string.get("urgency_level") < 6:
            print("Urgency level is invalid.")
            flag_reasons.append("FLAG: Urgency level is out of range (1-5).")
            flag = "FLAG"

        # validate shelter names against CSV file
        criterias_met = json_string.get("criterias_met", [])
        ai_shelter_names = {item["shelter_name"] for item in criterias_met}
        shelter_count = 0
        target_count = len(criterias_met)
        accepted_shelter_names = []
        with open(CSV_FILENAME, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["Shelter Name"] in ai_shelter_names:
                    print("Shelter name is valid.")
                    shelter_count += 1
                    accepted_shelter_names.append(row["Shelter Name"])
        # if there is an incorrect shelter name, the name will be added to flag_reasons
        if shelter_count < target_count:
            print("Shelter name is invalid.")
            for i in criterias_met:
                if i["shelter_name"] not in accepted_shelter_names:
                    flag_reason = f"FLAG: {i['shelter_name']} does not exist."
                    flag_reasons.append(flag_reason)
            flag = "FLAG"

        # validate ai_confidence_score and suitability_score within range
        for i in criterias_met:
            if not 0 <= i.get("ai_confidence_score", 0) <= 1:
                print("AI confidence score is invalid.")
                flag_reasons.append(
                    f"FLAG: AI confidence score for {i['shelter_name']} is out of range (0-1)."
                )
                flag = "FLAG"
            if not 0 <= i.get("suitability_score", 0) <= 100:
                print("Suitability score is invalid.")
                flag_reasons.append(
                    f"FLAG: AI suitability score for {i['shelter_name']} is out of range (0-100)."
                )
                flag = "FLAG"
            # sanitize and validate min_age and max_age
            min_age = i.get("min_age", 0)
            max_age = i.get("max_age", 120)
            if  min_age > max_age or min_age < 0 or min_age > 100 or max_age < 1 or max_age > 120:
                flag_reasons.append(f"FLAG: AI age range for {i['shelter_name']} is out of bounds.")
                flag = "FLAG"
            # sanitize and validate gender_restriction
            if i.get("gender_restriction") not in ["Male", "Female", "any"]:
                flag_reasons.append(f"FLAG: AI gender restriction for {i['shelter_name']} is invalid.")
                flag = "FLAG"




        print(flag_reasons)
        return flag, flag_reasons

    except Exception as e:
        print("Error validating AI recommendation:", e)
        flag = "FLAG"
        flag_reasons.append("FLAG: Unexpected error occurred.")


def calculate_suitability_score(client_data, shelter_data):
    score = 0
    reasons = []

    # # Check age requirement
    # if client_data["age"] < shelter_data["min_age"]:
    #     score -= 10
    #     reasons.append(f"Client age {client_data['age']} is below minimum age {shelter_data['min_age']}.")
    # elif client_data["age"] > shelter_data["max_age"]:
    #     score -= 10
    #     reasons.append(f"Client age {client_data['age']} is above maximum age {shelter_data['max_age']}.")

    # # Check gender requirement
    # if shelter_data["gender_restriction"] and client_data["gender"] != shelter_data["gender_restriction"]:
    #     score -= 10
    #     reasons.append(f"Client gender {client_data['gender']} does not match shelter gender restriction {shelter_data['gender_restriction']}.")

    # # Check family requirement
    # if shelter_data["family_only"] and client_data["dependents"] == 0:
    #     score -= 10
    #     reasons.append("Client has no dependents but shelter requires families.")

    # # Additional criteria checks can be added here

    # return score, reasons


def json_to_dict(json_string):
    print("hello")


# with open("stuff.json", "r") as f:
#     stuff = json.load(f)
# validate_ai_recommendation(json.dumps(stuff))
# flag, flag_reasons = validate_ai_recommendation(stuff)


# when do we flag an ai response, when only 1 shelter recommended hallucinates?
# Decide an outcome: flag, score, route, accept, or reject
# compare user input age to the requirement
# Has 0 dependents but shelter requires Families (-999.0) (Disqualified)

# NEED GENDER, MIN AGE, MAX AGE, FAMILY ONLY, PETS ALLOWED

# if rules["gender_restriction"] and client_gender and client_gender != rules["gender_restriction"]:
# return -999.0, [f"REJECT: Gender mismatch for {shelter_name} (Requires {rules['gender_restriction']})."]

# if rules["family_only"] and client_dependents == 0:
# return -999.0, [f"REJECT: {shelter_name} requires dependents/families."]

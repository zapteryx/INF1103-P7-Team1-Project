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
    flag = "FLAG"
    try:
        # data = json.loads(json_string)
        # validate urgency level within range 1-5
        if not 0 < json_string.get("urgency_level") < 6:
            print("Urgency level is invalid.")
            flag_reasons.append("FLAG: Urgency level is out of range (1-5).")
            flag = "REJECT"

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
            flag = "REJECT"

        # validate ai_confidence_score and suitability_score within range
        for i in criterias_met:
            if not 0 <= i.get("ai_confidence_score", 0) <= 1:
                print("AI confidence score is invalid.")
                flag_reasons.append(
                    f"FLAG: AI confidence score for {i['shelter_name']} is out of range (0-1)."
                )
                flag = "REJECT"
            if not 0 <= i.get("suitability_score", 0) <= 100:
                print("Suitability score is invalid.")
                flag_reasons.append(
                    f"FLAG: Suitability score for {i['shelter_name']} is out of range (0-100)."
                )
                flag = "REJECT"
                
        return flag, flag_reasons

    except Exception as e:
        print("Error validating AI recommendation:", e)
        flag = "REJECT"
        flag_reasons.append("FLAG: Unexpected error occurred.")


def json_to_dict(json_string):
    print("hello")


with open("stuff.json", "r") as f:
    stuff = json.load(f)
# validate_ai_recommendation(json.dumps(stuff))
flag, flag_reasons = validate_ai_recommendation(stuff)


# when do we flag an ai response, when only 1 shelter recommended hallucinates?
# Decide an outcome: flag, score, route, accept, or reject

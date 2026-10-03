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
        shelter_quantity = 0
        target_quantity = len(json_string.get("criterias_met", []))
        accepted_shelter_names = []
        with open(CSV_FILENAME, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                for i in json_string.get("criterias_met", []):
                    if row["Shelter Name"] == i["shelter_name"]:
                        print("Shelter name is valid.")
                        shelter_quantity += 1
                        accepted_shelter_names.append(i["shelter_name"])
                        break
        # if there is an incorrect shelter name, the name will be added to flag_reasons
        if shelter_quantity < target_quantity:
            print("Shelter name is invalid.")
            for i in json_string.get("criterias_met", []):
                if i["shelter_name"] not in accepted_shelter_names:
                    flag_reason = f"FLAG: '{i['shelter_name']}' does not exist."
                    flag_reasons.append(flag_reason)
            flag = "REJECT"

    except Exception as e:
        print("Error validating AI recommendation:", e)


def json_to_dict(json_string):
    print("hello")


with open("stuff.json", "r") as f:
    stuff = json.load(f)
# validate_ai_recommendation(json.dumps(stuff))
validate_ai_recommendation(stuff)




# when do we flag an ai response, when only 1 shelter recommended hallucinates?
# Decide an outcome: flag, score, route, accept, or reject

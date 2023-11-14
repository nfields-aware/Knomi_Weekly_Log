import json
import os
import pymongo 

# strips the json
def parse_json(json_input):
    try:
        data = json.loads(json_input)

        mrz_name = None
        given_name = None

        #find the necessary fields
        for field in data.get("documentsInfoResults", {}).get("documentAuthenticationResult", {}).get("fieldType", []):
            if field.get("name") == "Surname And Given Names":
                mrz_name = field.get("fieldResult", {}).get("mrz")
            if field.get("name") == "Given names":
                given_name = field.get("fieldResult", {}).get("mrz")

        # creates results
        result = {
            "MRZName": mrz_name,
            "GivenName": given_name,
            "DocumentType": data.get("documentsInfoResults", {}).get("documentAuthenticationResult", {}).get("documentType", None),
            "OverallResult": data.get("documentsInfoResults", {}).get("documentAuthenticationResult", {}).get("overallResult", None),
            "FacialMatchResults": data.get("facialMatchResults", None),
            "FaceLivenessResults": data.get("faceLivenessResults", None)
        }

        # Filter out entries that don't have the necessary data
        if not any([result["MRZName"], result["GivenName"]]):
            return None
        return result
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return None

#connect to mongo
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["dva_db"]
collection = db["weekly_logs"]

# root log directory 
root_directory = '/home/ec2-user/Knomi-Weekly-Logs'

# recursive parse
for subdir, dirs, files in os.walk(root_directory):
    for filename in files:
        if filename.endswith(".json"):
            file_path = os.path.join(subdir, filename)
            try:
                with open(file_path, 'r') as file:
                    json_data = file.read()
                    parsed_data = parse_json(json_data)
                    if parsed_data:
                        collection.insert_one(parsed_data)
                        print(f"Data from {file_path} inserted into MongoDB.")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

#final message
print("All JSON files processed.")
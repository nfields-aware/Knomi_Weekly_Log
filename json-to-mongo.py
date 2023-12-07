import json
import os
import pymongo
import zipfile
import datetime
import shutil

#strips json into the future columns

def parse_json(json_input, file_date):
    data = json.loads(json_input)
    mrz_name = None
    given_name = None
    for field in data.get("documentsInfoResults", {}).get("documentAuthenticationResult", {}).get("fieldType", []):
        if field.get("name") == "Surname And Given Names":
            mrz_name = field.get("fieldResult", {}).get("mrz")
        if field.get("name") == "Given names":
            given_name = field.get("fieldResult", {}).get("mrz")
    result = {
	"MRZName": mrz_name,
        "GivenName": given_name,
        "DocumentType": data.get("documentsInfoResults", {}).get("documentAuthenticationResult", {}).get("documentType", None),
        "DocumentResult": data.get("documentsInfoResults", {}).get("documentAuthenticationResult", {}).get("overallResult", None),
        "FacialMatchResults": data.get("facialMatchResults", None),
        "FaceLivenessResults": data.get("faceLivenessResults", None),
        "DateString": file_date,  # Original date string
        "Date": datetime.datetime.strptime(file_date, '%B %d, %Y')  # Converted to BSON date format
    }
    if not any([result["MRZName"], result["GivenName"]]):
        return None
    return result

def find_latest_zip(directory):
    zip_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.zip')]
    if not zip_files:
        return None
    return max(zip_files, key=os.path.getctime)

def unzip_file(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

#takes date from file name 
def extract_date_from_filename(filename):
    try:
        date_str = filename.split('.')[2].split('_')[0]
        return datetime.datetime.strptime(date_str, '%Y-%m-%d').strftime('%B %d, %Y')
    except ValueError as e:
        print(f"Error extracting date from filename {filename}: {e}")
        return None

#moves the log zip 
def move_and_process_zip(zip_file_path, temp_dir):
    if not temp_dir.endswith('/'):
     temp_dir += '/'

    # move the zip file to the temp directory
    temp_zip_path = os.path.join(temp_dir, os.path.basename(zip_file_path))
    shutil.move(zip_file_path, temp_zip_path)

    # unzip the file in the temp directory
    unzip_file(temp_zip_path, temp_dir)

    # process the JSON files into Mongo
    for subdir, dirs, files in os.walk(temp_dir):
        for filename in files:
            if filename.endswith(".json"):
                file_path = os.path.join(subdir, filename)
                file_date = extract_date_from_filename(filename)
                with open(file_path, 'r') as file:
                    json_data = file.read()
                    parsed_data = parse_json(json_data, file_date)
                    if parsed_data:
                        #prevents duplicate data
                        if not collection.find_one({"MRZName": parsed_data["MRZName"], "GivenName": parsed_data["GivenName"], "Date": parsed_data["Date"]}):
                            collection.insert_one(parsed_data)
                            print(f"Data from {file_path} inserted into MongoDB.")


  # deletes the zip file from the temp directory [will uncomment this if cron jobs are successful]
    #os.remove(temp_zip_path) 

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["dva_db"]
collection = db["dva_logs"]

latest_zip = find_latest_zip('/home/ec2-user/Knomi-Weekly-Logs')
if latest_zip:
    unzip_dir = '/home/ec2-user/Knomi-Weekly-Logs/temp'
    move_and_process_zip(latest_zip, unzip_dir)

print("All JSON files processed.")

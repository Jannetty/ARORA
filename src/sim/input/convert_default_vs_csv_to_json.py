import csv
import json

csv_file_path = "default_vs.csv"  # Replace with your actual CSV file path
json_file_path = "default_vs.json"

# Read the CSV and convert to JSON
data = []

with open(csv_file_path, mode="r") as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        data.append(row)

# Write the JSON data to a file
with open(json_file_path, mode="w") as json_file:
    json.dump(data, json_file, indent=4)

print(f"CSV data has been converted to JSON and saved to {json_file_path}")

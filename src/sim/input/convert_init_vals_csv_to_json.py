import csv
import json

# Define the paths to your CSV and JSON files
csv_file_path = "default_init_vals.csv"
json_file_path = "init_vals.json"

data = []


# Function to clean and convert neighbors string
def clean_neighbors(neighbors_str):
    neighbors_str = neighbors_str.replace("[", "").replace("]", "").replace("c", "").split(",")
    return [f"c{n.strip()}" for n in neighbors_str]


# Read the CSV file and convert it to a list of dictionaries
with open(csv_file_path, mode="r") as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        # Convert string representations of lists and booleans to actual lists and booleans
        row["arr_hist"] = json.loads(row["arr_hist"])
        row["growing"] = row["growing"].upper() == "FALSE"  # Adjusted to match the given data
        row["vertices"] = json.loads(row["vertices"])
        row["neighbors"] = clean_neighbors(row["neighbors"])
        data.append(row)

# Write the list of dictionaries to a JSON file
with open(json_file_path, mode="w") as json_file:
    json.dump(data, json_file, indent=4)

print(f"CSV data successfully converted to JSON and saved to {json_file_path}")

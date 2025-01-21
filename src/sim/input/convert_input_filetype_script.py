import csv
import json
import ast

# Read the CSV file
csv_file_path = "indep_syn_deg_init_vals.csv"
json_file_path = "indep_syn_deg_init_vals.json"

# Initialize an empty list to store the rows
data = []


# Helper function to parse list-like strings and convert elements to integers
def parse_list_string(s: str) -> list[int]:
    return [int(x) for x in s.strip("[]").split(",")]


# Open the CSV file and read the contents
with open(csv_file_path, mode="r") as csv_file:
    csv_reader = csv.DictReader(csv_file)

    # Iterate over each row in the CSV
    for row in csv_reader:
        try:
            # Manually parse list-like strings and convert to correct data types
            row["auxin"] = float(row["auxin"])
            row["arr"] = int(row["arr"])
            row["al"] = int(row["al"])
            row["pin"] = float(row["pin"])
            row["pina"] = float(row["pina"])
            row["pinb"] = float(row["pinb"])
            row["pinl"] = float(row["pinl"])
            row["pinm"] = float(row["pinm"])
            row["k1"] = float(row["k1"])
            row["k2"] = float(row["k2"])
            row["k3"] = float(row["k3"])
            row["k4"] = float(row["k4"])
            row["k5"] = float(row["k5"])
            row["k6"] = float(row["k6"])
            row["ks_aux"] = float(row["ks_aux"])
            row["kd_aux"] = float(row["kd_aux"])
            row["ks_arr"] = float(row["ks_arr"])
            row["kd_arr"] = float(row["kd_arr"])
            row["ks_pinu"] = float(row["ks_pinu"])
            row["kd_pinu"] = float(row["kd_pinu"])
            row["kd_pinloc"] = float(row["kd_pinloc"])
            row["ks_auxlax"] = float(row["ks_auxlax"])
            row["kd_auxlax"] = float(row["kd_auxlax"])
            row["auxin_w"] = int(row["auxin_w"])
            row["arr_hist"] = parse_list_string(row["arr_hist"])
            row["growing"] = row["growing"] == "TRUE"
            row["vertices"] = parse_list_string(row["vertices"])

            # Parsing neighbors and ensuring no leading/trailing spaces
            row["neighbors"] = [
                neighbor.strip() for neighbor in row["neighbors"].strip("[]").split(",")
            ]

        except ValueError as e:
            print(f"Error converting row: {row}")
            print(f"Error message: {e}")
            continue

        # Append the row to the data list
        data.append(row)

# Write the data to a JSON file
with open(json_file_path, mode="w") as json_file:
    json.dump(data, json_file, indent=4)

print(f"Data successfully converted from CSV to JSON and saved to {json_file_path}")


# Read the CSV file
csv_file_path = "default_init_vals.csv"
json_file_path = "default_init_vals.json"

# Initialize an empty list to store the rows
data = []

# Open the CSV file and read the contents
with open(csv_file_path, mode="r") as csv_file:
    csv_reader = csv.DictReader(csv_file)

    # Iterate over each row in the CSV
    for row in csv_reader:
        try:
            # Manually parse list-like strings and convert to correct data types
            row["auxin"] = float(row["auxin"])
            row["arr"] = int(row["arr"])
            row["al"] = int(row["al"])
            row["pin"] = float(row["pin"])
            row["pina"] = float(row["pina"])
            row["pinb"] = float(row["pinb"])
            row["pinl"] = float(row["pinl"])
            row["pinm"] = float(row["pinm"])
            row["k1"] = float(row["k1"])
            row["k2"] = float(row["k2"])
            row["k3"] = float(row["k3"])
            row["k4"] = float(row["k4"])
            row["k5"] = float(row["k5"])
            row["k6"] = float(row["k6"])
            row["k_s"] = float(row["k_s"])
            row["k_d"] = float(row["k_d"])
            row["auxin_w"] = int(row["auxin_w"])
            row["arr_hist"] = parse_list_string(row["arr_hist"])
            row["growing"] = row["growing"] == "TRUE"
            row["vertices"] = parse_list_string(row["vertices"])

            # Parsing neighbors and ensuring no leading/trailing spaces
            row["neighbors"] = [
                neighbor.strip() for neighbor in row["neighbors"].strip("[]").split(",")
            ]

        except ValueError as e:
            print(f"Error converting row: {row}")
            print(f"Error message: {e}")
            continue

        # Append the row to the data list
        data.append(row)

# Write the data to a JSON file
with open(json_file_path, mode="w") as json_file:
    json.dump(data, json_file, indent=4)

print(f"Data successfully converted from CSV to JSON and saved to {json_file_path}")

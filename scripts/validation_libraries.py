import pandas as pd
import os
import subprocess
import json
from jsonschema import ValidationError
import sys
import re 
import numpy as np
import csv

# Read the common_libraries.tsv from the pull request into a DataFrame
df_pr = pd.read_csv(os.environ["LIBRARIES_PATH"], sep="\t")

# Fetch the main branch from the repository
subprocess.run(["git", "fetch", "origin", "main"])

# Checkout the common_libraries.tsv from the main branch
subprocess.run(["git", "checkout", "FETCH_HEAD", "--", os.environ["LIBRARIES_PATH"]])

# Read the common_libraries.tsv from the main branch into a DataFrame
df_fork = pd.read_csv(os.environ["LIBRARIES_PATH"], sep="\t")

# Extract the new rows that have been added in the pull request
new_rows = df_pr.loc[df_pr.index[len(df_fork):]]

# Create a copy of the df_fork and df_pr for checking
df_fork_check = df_fork.copy()
df_pr_check = df_pr.drop(new_rows.index)

# Print the content of the new rows added in the pull request
print("\nContent of new_rows:")
print(new_rows)
print()

# Compare the DataFrames of the pull request and the main branch
comparison_result = df_pr_check.compare(df_fork_check)
if comparison_result.empty:
    print("\033[38;5;40mThe old rows haven't been changed, now let's validate new rows\033[0m")
    print()
else:
    print("\033[31mThe old rows have been changed:\033[0m")
    print(comparison_result)
    sys.exit(1)

# Define a function to validate a cell value based on the given schema
def is_valid(cell, schema):

    # Validate the attribute 'type' if specified in the schema
    if 'type' in schema:
        if schema['type'] == 'string' and not isinstance(cell, str):
            print(f"Error in column {column} in cell '{cell}' -> Invalid data type. Expected type: {schema['type']}")
            return False
        elif schema['type'] == 'integer' and not isinstance(cell, int):
            print(f"Error in column {column} in cell '{cell}' -> Invalid data type. Expected type: {schema['type']}")
            return False

    # Validate the attribute 'pattern' if specified in the schema
    if 'pattern' in schema and not re.match(schema['pattern'], str(cell)):
        print(f"Error in column {column} in cell '{cell}' -> Doesn't fit the expected pattern: {schema['pattern']}")
        return False

    # Validate the attribute 'enum' if specified in the schema
    if 'enum' in schema and cell not in schema['enum']:
        print(f"Error in column {column} in cell '{cell}' -> Value is not from the list of possible values: {schema['enum']}")
        return False

    return True

# List of columns to be removed from validation
columns_to_remove = ["publication_year", "library_concentration", "PCR_cycle_count", "read_count", "download_sizes"]
columns = new_rows.columns.drop(columns_to_remove)

# Replace nan values with None in new_rows
new_rows.replace({np.nan: None}, inplace=True)

# Define the path to the JSON schema files
schemas_path = os.path.join(os.environ["GITHUB_WORKSPACE"], 'schemas_libraries')

# Initialize a flag to track if any validation fails
error_flag = False

# Iterate through the columns and apply validation based on corresponding JSON schema
for column in columns:
    # Find and read the corresponding JSON file for the given column
    json_file = [file for file in os.listdir(schemas_path) if file.endswith('.json') and os.path.splitext(file)[0] == column]
    json_file_path = os.path.join(schemas_path, json_file[0])
    with open(json_file_path, 'r') as file:
        schema = json.load(file)

    # Apply the validation function to the current column using the loaded schema
    validation_results = new_rows[column].apply(is_valid, schema=schema['properties'][column])
    if not all(validation_results):
        error_flag = True
    else:
        print('Successful column validation:', column)
    print()

# Print the final validation result, exit with an error code if any validation failed
if error_flag:
    print("\033[31mFailed validation of common_libraries.tsv\033[0m")
    # sys.exit(1)
else:
    print("\033[38;5;40mSuccessful validation of common_libraries.tsv\033[0m")

# Все, что выше, правильно работает

def convert_value(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        try:
            return float(value)
        except (ValueError, TypeError):
            return value

def read_tsv_with_mixed_types(file_path, columns):
    result = {col: [] for col in columns}

    with open(file_path) as tsvfile:
        data = csv.DictReader(tsvfile, delimiter="\t")

        for row in data:
            for col, check in columns.items():
                if check:
                    result[col].append(convert_value(row[col]))
                else:
                    result[col].append(row[col])

    return result

columns_to_check = {
    "publication_year": True,
    "library_concentration": True,
    "PCR_cycle_count": True,
    "read_count": True,
    "download_sizes": True,
}

data = read_tsv_with_mixed_types(os.environ["LIBRARIES_PATH"], columns_to_check)
print(data)
import pandas as pd
import os, sys, json, subprocess
from jsonschema import validate, ValidationError

# Read the DataFrame used for comparison purposes
def read_dataframe_for_compare(path):
    return pd.read_csv(path, sep="\t")

# Read the DataFrame used for validation purposes with specific data types
def read_dataframe_for_validation(path):
    return pd.read_csv(path, sep="\t",
                       dtype={
                           "publication_year": str, "strand_type": str, "library_polymerase": str,
                           "library_concentration": str, "library_treatment": str, "PCR_cycle_count": str,
                           "read_count": str, "download_sizes": str
                       },
                       keep_default_na=False)

# Fetch and checkout a specific branch in git
def fetch_and_checkout_branch(branch_name, path):
    subprocess.run(["git", "fetch", "origin", branch_name])
    subprocess.run(["git", "checkout", "FETCH_HEAD", "--", path])

# Compare two DataFrames and return the differences
def compare_dataframes(df1, df2):
    df1_check = df1.drop(df1.loc[df1.index[len(df2):]].index)
    comparison_result = df1_check.compare(df2)
    return comparison_result

# Validate new rows based on JSON schemas
def validate_new_rows(new_rows, schemas_path, starting_index):
    columns = new_rows.columns
    validation_results = {}
    error_value = False

    # Loop through each column and validate against respective schema
    for column in columns:
        json_file = [file for file in os.listdir(schemas_path) if file.endswith('.json') and os.path.splitext(file)[0] == column]
        json_file_path = os.path.join(schemas_path, json_file[0])
        with open(json_file_path, 'r') as file:
            schema = json.load(file)
        column_results = []
        for index, value in enumerate(new_rows[column], start=starting_index):
            try:
                validate(instance=value, schema=schema)
                column_results.append(f"Valid (Row {index})")
            except ValidationError as e:
                error_message = e.message.replace('\\\\', '\\')
                column_results.append(f"Invalid (Row {index}): {error_message}")
                error_value = True
        validation_results[column] = column_results
    return validation_results, error_value

# Main execution
def main():
    # Read the DataFrame for PR and validation
    LIBRARIES_PATH = os.environ["LIBRARIES_PATH"]
    df_pr = read_dataframe_for_compare(LIBRARIES_PATH)
    df_pr_ = read_dataframe_for_validation(LIBRARIES_PATH)

    # Fetch and checkout to main branch, then read the fork's DataFrame
    fetch_and_checkout_branch("main", LIBRARIES_PATH)
    df_fork = read_dataframe_for_compare(LIBRARIES_PATH)

    # Compare PR's and fork's DataFrame
    comparison_result = compare_dataframes(df_pr, df_fork)

    if comparison_result.empty:
        print("\033[38;5;40mThe old rows haven't been changed, now let's validate new rows\033[0m")
    else:
        print("\033[31mThe old rows have been changed:\033[0m", comparison_result)
        sys.exit(1)

    # Extract new rows for validation
    new_rows = df_pr_.loc[df_pr_.index[len(df_fork):]]
    print("Content of new_rows:\n", new_rows)

    # Validate the new rows using schemas
    schemas_path = os.path.join(os.environ["GITHUB_WORKSPACE"], 'schemas_libraries')
    validation_results, error_value = validate_new_rows(new_rows, schemas_path, df_fork.shape[0])

    # Print the validation results
    formatted_output = json.dumps(validation_results, ensure_ascii=False, indent=1)
    print(formatted_output)

    if error_value:
        print("\033[31mInvalid values found\033[0m")
        exit(1)
    else:
        print("\033[38;5;40mNo invalid values found\033[0m")


if __name__ == "__main__":
    main()
import pandas as pd
import argparse, io, os, sys, json, subprocess
from jsonschema import validate, ValidationError
from collections import defaultdict

# Read the DataFrame used for comparison purposes
def read_dataframe_for_compare(path):
    return pd.read_csv(path, sep="\t", dtype=str)

# Read the DataFrame used for validation purposes with specific data types
def read_dataframe_for_validation(path):
    return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Default directory with the JSON schemas: $GITHUB_WORKSPACE in CI, the repository root otherwise
def default_schemas_dir(name):
    return os.path.join(os.environ.get("GITHUB_WORKSPACE", REPO_ROOT), name)

# Read the base version of the table without touching the working tree:
# from a file, from a git ref, or (default, as in CI) from origin/main after a fetch
def read_base_dataframe(path, base_ref=None, base_file=None):
    if base_file:
        return read_dataframe_for_compare(base_file)
    if base_ref is None:
        subprocess.run(["git", "fetch", "origin", "main"], check=True)
        base_ref = "FETCH_HEAD"
    content = subprocess.run(
        ["git", "show", f"{base_ref}:./{os.path.relpath(path)}"],
        check=True, capture_output=True, text=True, encoding="utf-8",
    ).stdout
    return read_dataframe_for_compare(io.StringIO(content))

# Compare two DataFrames and return the differences
def compare_dataframes(df1, df2):
    df1_check = df1.drop(df1.loc[df1.index[len(df2):]].index)
    comparison_result = df1_check.compare(df2)
    comparison_result.index += 2
    return comparison_result

# Return a dictionary that groups the indices of duplicate rows
def find_duplicate_rows(df):
    duplicated_rows = df[df.duplicated(keep=False)]
    duplicate_index_groups = defaultdict(list)
    for index, row in duplicated_rows.iterrows():
        duplicate_index_groups[tuple(row)].append(index+2)
    return {k: v for k, v in duplicate_index_groups.items() if len(v) > 1}

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
            except ValidationError as e:
                error_message = e.message.replace('\\\\', '\\')
                column_results.append(f"Invalid (Row {index+2}): {error_message}")
                error_value = True
        if column_results:
            validation_results[column] = column_results
    return validation_results, error_value

# Command-line arguments; the CI environment variables are used as defaults
def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Check that old rows of the samples table are unchanged and validate the appended rows against the JSON schemas.")
    parser.add_argument("--table", default=os.environ.get("SAMPLES_PATH", "common_samples/common_samples.tsv"),
                        help="samples table to check (default: $SAMPLES_PATH or %(default)s)")
    parser.add_argument("--schemas", default=default_schemas_dir("schemas_samples"),
                        help="directory with one JSON schema per column (default: %(default)s)")
    base = parser.add_mutually_exclusive_group()
    base.add_argument("--base-ref",
                      help="git ref with the accepted version of the table, e.g. main or upstream/main "
                           "(read with git show, no fetch); default: fetch origin main")
    base.add_argument("--base-file",
                      help="file with the accepted version of the table (no git access)")
    return parser.parse_args(argv)

# Main execution
def main(argv=None):
    args = parse_args(argv)

    # Read the DataFrame for PR and validation
    df_pr = read_dataframe_for_compare(args.table)
    df_pr_ = read_dataframe_for_validation(args.table)

    # Read the accepted (base branch) version of the table
    df_fork = read_base_dataframe(args.table, args.base_ref, args.base_file)

    # Compare PR's and fork's DataFrame
    comparison_result = compare_dataframes(df_pr, df_fork)
    if comparison_result.empty:
        print("\033[38;5;40mThe old rows haven't been changed\033[0m")
    else:
        print("\033[31mThe old rows have been changed:\033[0m\n", comparison_result)
        sys.exit(1)

    # Duplicate rows check
    duplicate_index_groups = find_duplicate_rows(df_pr_)
    if duplicate_index_groups:
        print("\033[31mDuplicate rows exist: " + ', '.join(f"rows {tuple(indices)}" for indices in duplicate_index_groups.values()) + "\033[0m")
        sys.exit(1)
    else:
        print("\033[38;5;40mDuplicate rows not found\033[0m")
    
    # Extract new rows for validation
    new_rows = df_pr_.loc[df_pr_.index > df_fork.index.max()]
    new_rows.index = range(len(df_fork) + 2, len(df_fork) + 2 + len(new_rows))
    print("Content of new_rows:\n", new_rows)

    # Validate the new rows using schemas
    schemas_path = args.schemas
    validation_results, error_value = validate_new_rows(new_rows, schemas_path, df_fork.shape[0])

    # Print the validation results
    if validation_results:
        formatted_output = json.dumps(validation_results, ensure_ascii=False, indent=1)
        print(formatted_output)

    if error_value:
        print("\033[31mInvalid values found\033[0m")
        sys.exit(1)
    else:
        print("\033[38;5;40mNo invalid values found\033[0m")


if __name__ == "__main__":
    main()

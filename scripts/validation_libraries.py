import pandas as pd
import numpy as np
import os, sys, re, json, subprocess
from jsonschema import validate, ValidationError
import logging

# Настройка логгирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def read_dataframe_from_path(path):
    return pd.read_csv(path, sep="\t")


def read_dataframe_for_validation(path):
    return pd.read_csv(path, sep="\t",
                       dtype={
                           "publication_year": str,
                           "strand_type": str,
                           "library_polymerase": str,
                           "library_concentration": str,
                           "library_treatment": str,
                           "PCR_cycle_count": str,
                           "read_count": str,
                           "download_sizes": str
                       },
                       keep_default_na=False)


def fetch_and_checkout_branch(branch_name, path):
    subprocess.run(["git", "fetch", "origin", branch_name])
    subprocess.run(["git", "checkout", "FETCH_HEAD", "--", path])


def compare_dataframes(df1, df2):
    df1_check = df1.drop(df1.loc[df1.index[len(df2):]].index)
    comparison_result = df1_check.compare(df2)
    return comparison_result


def validate_new_rows(new_rows, schemas_path):
    columns = new_rows.columns
    validation_results = {}
    error_value = False

    for column in columns:
        json_file = [file for file in os.listdir(schemas_path) if file.endswith('.json') and os.path.splitext(file)[0] == column]
        json_file_path = os.path.join(schemas_path, json_file[0])
        with open(json_file_path, 'r') as file:
            schema = json.load(file)
        column_results = []
        for index, value in enumerate(new_rows[column], start=df_fork.shape[0]):
            try:
                validate(instance=value, schema=schema)
                column_results.append(f"Valid (Row {index})")
            except ValidationError as e:
                error_message = e.message.replace('\\\\', '\\')
                column_results.append(f"Invalid (Row {index}): {error_message}")
                error_value = True
        validation_results[column] = column_results

    return validation_results, error_value


def main():
    LIBRARIES_PATH = os.environ["LIBRARIES_PATH"]
    df_pr = read_dataframe_from_path(LIBRARIES_PATH)
    df_pr_ = read_dataframe_for_validation(LIBRARIES_PATH)

    fetch_and_checkout_branch("main", LIBRARIES_PATH)
    df_fork = read_dataframe_from_path(LIBRARIES_PATH)

    comparison_result = compare_dataframes(df_pr, df_fork)

    if comparison_result.empty:
        logging.info("The old rows haven't been changed, now let's validate new rows")
    else:
        logging.error("The old rows have been changed:")
        logging.error(comparison_result)
        sys.exit(1)

    new_rows = df_pr_.loc[df_pr_.index[len(df_fork):]]
    logging.info("\nContent of new_rows:")
    logging.info(new_rows)

    schemas_path = os.path.join(os.environ["GITHUB_WORKSPACE"], 'schemas_libraries')
    validation_results, error_value = validate_new_rows(new_rows, schemas_path)

    formatted_output = json.dumps(validation_results, ensure_ascii=False, indent=1)
    logging.info(formatted_output)

    if error_value:
        logging.error("Invalid values found")
        exit(1)
    else:
        logging.info("No invalid values found")


if __name__ == "__main__":
    main()

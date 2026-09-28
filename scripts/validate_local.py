"""Validate every row of both tables locally, on the current checkout.

validation_samples.py / validation_libraries.py are written for CI: they only
check rows appended after origin/main and require GITHUB_WORKSPACE and
SAMPLES_PATH/LIBRARIES_PATH env vars plus a git fetch against origin. This
script reuses their schema-validation, duplicate-row and uniqueness checks
(and validation_srs.py's cross-table check) but runs them against the whole
table, with no env vars or network access required.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from validation_samples import (
    read_dataframe_for_validation as read_samples_df,
    find_duplicate_rows,
    validate_new_rows,
)
from validation_libraries import (
    read_dataframe_for_validation as read_libraries_df,
    check_column_uniqueness,
)
from validation_srs import check_srs


def report_schema_errors(label, validation_results):
    if not validation_results:
        print(f"[{label}] no schema violations")
        return
    print(f"[{label}] schema violations:")
    print(json.dumps(validation_results, ensure_ascii=False, indent=1))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", default="common_samples/common_samples.tsv")
    parser.add_argument("--libraries", default="common_libraries/common_libraries.tsv")
    parser.add_argument("--schemas-samples", default="schemas_samples")
    parser.add_argument("--schemas-libraries", default="schemas_libraries")
    args = parser.parse_args()

    had_errors = False

    df_samples = read_samples_df(args.samples)
    dup_samples = find_duplicate_rows(df_samples)
    if dup_samples:
        had_errors = True
        print(f"[samples] duplicate rows: {dup_samples}")
    else:
        print(f"[samples] no duplicate rows ({len(df_samples)} rows checked)")

    results_samples, err_samples = validate_new_rows(df_samples, args.schemas_samples, starting_index=0)
    had_errors = had_errors or err_samples
    report_schema_errors("samples", results_samples)

    df_libraries = read_libraries_df(args.libraries)
    dup_libraries = find_duplicate_rows(df_libraries)
    if dup_libraries:
        had_errors = True
        print(f"[libraries] duplicate rows: {dup_libraries}")
    else:
        print(f"[libraries] no duplicate rows ({len(df_libraries)} rows checked)")

    unique_cols = ["download_links", "download_md5s", "archive_data_accession"]
    non_unique = check_column_uniqueness(df_libraries, unique_cols)
    if non_unique:
        had_errors = True
        print(f"[libraries] non-unique columns: {dict(non_unique)}")
    else:
        print(f"[libraries] columns {unique_cols} are all unique")

    results_libraries, err_libraries = validate_new_rows(df_libraries, args.schemas_libraries, starting_index=0)
    had_errors = had_errors or err_libraries
    report_schema_errors("libraries", results_libraries)

    valid_srs, message = check_srs(df_samples["archive_accession"], df_libraries["archive_accession"])
    print(message)
    had_errors = had_errors or not valid_srs

    sys.exit(1 if had_errors else 0)


if __name__ == "__main__":
    main()

import pandas as pd
import os, sys

# Read the DataFrame used for comparison purposes
def read_dataframe_for_compare(path):
    return pd.read_csv(path, sep="\t", dtype=str)

# Validation of SRS
def check_srs(samples, libraries):
    set_s = set(samples)
    set_l = set(libraries)
    error_messages = []
    
    # Проверяем, что все значения из libraries присутствуют в samples
    missing_from_samples = set_l - set_s
    for index, value in enumerate(libraries):
        if value in missing_from_samples and f"Invalid SRS of libraries (Row {index+2}): {value} is not in samples" not in error_messages:
            error_messages.append(f"Invalid SRS of libraries (Row {index+2}): {value} is not in samples")
    
    # Проверяем, что для каждого значения из samples есть хотя бы одно соответствующее значение в libraries
    missing_from_libraries = set_s - set_l
    for index, s in enumerate(samples):
        if s in missing_from_libraries and f"Invalid SRS of samples (Row {index+2}): {s} is not in libraries" not in error_messages:
            error_messages.append(f"Invalid SRS of samples (Row {index+2}): {s} is not in libraries")
    
    if not error_messages:
        return True, "\033[38;5;40mAll SRS values are valid\033[0m"
    else:
        return False, "\n".join(error_messages)

# Main execution
def main():
    # Read the SRS column to validation
    df_s = read_dataframe_for_compare(os.environ["SAMPLES_PATH"])
    df_l = read_dataframe_for_compare(os.environ["LIBRARIES_PATH"])
    valid, message = check_srs(df_s['archive_accession'], df_l['archive_accession'])
    
    # Print the validation results
    print(message)

    error_value = not valid
    if error_value:
        print("\033[31mInvalid values of SRS found\033[0m")
        sys.exit(1)
    else:
        print("\033[38;5;40mNo invalid values of SRS found\033[0m")


if __name__ == "__main__":
    main()
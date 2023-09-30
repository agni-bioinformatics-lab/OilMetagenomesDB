import pandas as pd
import os

# Read the DataFrame used for comparison purposes
def read_dataframe_for_compare(path):
    return pd.read_csv(path, sep="\t", dtype=str)

# Validation of SRS
def check_srs(samples, libraries):
    set_s = set(samples)
    set_l = set(libraries)
    
    # Проверяем, что все значения из libraries присутствуют в samples
    if not set_l.issubset(set_l):
        return False
    
    # Проверяем, что для каждого значения из samples есть хотя бы одно соответствующее значение в libraries
    for s in set_s:
        if s not in libraries:
            return False
    return True

# Main execution
def main():
    # Read the SRS column to validation
    df_s = read_dataframe_for_compare(os.environ["SAMPLES_PATH"])
    df_l = read_dataframe_for_compare(os.environ["LIBRARIES_PATH"])
    
    print(check_srs(df_s['archive_accession'], df_l['archive_accession']))
    print('df_s')
    print(df_s.shape)
    print('df_l')
    print(df_l.shape)
    
if __name__ == "__main__":
    main()
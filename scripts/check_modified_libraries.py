import pandas as pd
import os
import subprocess

# Load the file from the pull request
df_pr = pd.read_csv(os.environ["FILE_PATH"], sep="\t")

# Fetch the version of the file when the fork was created
subprocess.run(["git", "fetch", "origin", "main"])
subprocess.run(["git", "checkout", "FETCH_HEAD", "--", os.environ["FILE_PATH"]])

# Load the old file
df_fork = pd.read_csv(os.environ["FILE_PATH"], sep="\t")

# Merge the two DataFrames and create a new column '_merge' indicating where each row is from
merged = df_fork.merge(df_pr, how='outer', indicator=True)

# Check if any of the old rows have been modified or deleted
if (merged['_merge'] == 'left_only').any():
    print("\033[31mOld rows in common_libraries.tsv have been modified or deleted\033[0m")
    exit(1)

command = 'echo -e "\033[38;5;40mNo old rows have been modified or deleted in common_samples.tsv\033[0m"'
subprocess.call(command, shell=True)

new_rows = df_pr[~df_pr.isin(df_fork)].dropna()
print("new_rows")
print(new_rows)
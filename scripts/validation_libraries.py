import pandas as pd
import os
import subprocess
import json
from jsonschema import validate, ValidationError
import sys

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

# Compare the DataFrames of the pull request and the main branch
comparison_result = df_pr_check.compare(df_fork_check)
if comparison_result.empty:
    print("\033[38;5;40mThe old rows haven't been changed\033[0m")
else:
    print("\033[31mThe old rows have been changed:\033[0m")
    print(comparison_result)
    sys.exit(1)
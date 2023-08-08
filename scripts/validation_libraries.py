import pandas as pd
import os
import subprocess
import json
from jsonschema import validate, ValidationError
import sys

print("it's working")

# Load the file from the pull request
df_pr = pd.read_csv(os.environ["common_libraries/common_libraries.tsv"], sep="\t")

# Fetch the version of the file when the fork was created
subprocess.run(["git", "fetch", "origin", "main"])
subprocess.run(["git", "checkout", "FETCH_HEAD", "--", os.environ["/home/runner/work/OilMetagenomesDB/OilMetagenomesDB/common_libraries/common_libraries.tsv"]])

# Load the old file
df_fork = pd.read_csv(os.environ["/home/runner/work/OilMetagenomesDB/OilMetagenomesDB/common_libraries/common_libraries.tsv"], sep="\t")

new_rows = df_pr.loc[df_pr.index[len(df_fork):]]

df_fork_check = df_fork.copy()

# Drop new_rows from df_pr and save it to df_pr_check
df_pr_check = df_pr.drop(new_rows.index)

# Вывод содержимого таблиц
print('\ndf_fork_check')
print(df_fork_check)
print()
print('\ndf_pr_check')
print(df_pr_check)
print()

# Вывод содержимого new_rows
print("\nСодержимое new_rows:")
print(new_rows)

# Сравнение фреймов данных
comparison_result = df_pr_check.compare(df_fork_check)

# Вывод различий
if comparison_result.empty:
    print("CSV files are identical, let's continue validation")
else:
    print("Differences between CSV files:")
    print(comparison_result)
    sys.exit(1)
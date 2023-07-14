import pandas as pd
import os
import subprocess
import json
from jsonschema import validate, ValidationError
import sys

# Load the file from the pull request
df_pr = pd.read_csv(os.environ["FILE_PATH"], sep="\t")

# Fetch the version of the file when the fork was created
subprocess.run(["git", "fetch", "origin", "main"])
subprocess.run(["git", "checkout", "FETCH_HEAD", "--", os.environ["FILE_PATH"]])

# Load the old file
df_fork = pd.read_csv(os.environ["FILE_PATH"], sep="\t")

# Check string uniqueness in df_fork
if df_fork.duplicated().any():
    print("Rows are not unique")
    sys.exit(1)

new_rows = df_pr[~df_pr.isin(df_fork)].dropna()

df_fork_check = df_fork.copy()

# Drop new_rows from df_pr and save it to df_pr_check
df_pr_check = df_pr.drop(new_rows.index)

print('df_fork_check')
print(df_fork_check)
print('df_pr_check')
print(df_pr_check)

df_fork_check.reset_index(drop=True, inplace=True)
df_pr_check.reset_index(drop=True, inplace=True)

# Normalize the data in df_fork_check and df_pr_check
df_fork_check = df_fork_check.applymap(lambda x: x.strip() if isinstance(x, str) else x)
df_fork_check = df_fork_check.applymap(lambda x: x.lower() if isinstance(x, str) else x)

df_pr_check = df_pr_check.applymap(lambda x: x.strip() if isinstance(x, str) else x)
df_pr_check = df_pr_check.applymap(lambda x: x.lower() if isinstance(x, str) else x)

# Save df_pr_check to a CSV file
df_pr_check.to_csv("df_pr_check.csv", index=False)

# Save df_fork_check to a CSV file
df_fork_check.to_csv("df_fork_check.csv", index=False)
    
command = 'echo -n "\033[38;5;40mNo old rows have been modified or deleted in common_libraries.tsv\033[0m"'
subprocess.call(command, shell=True)

# Вывод содержимого new_rows
print("\nСодержимое new_rows:")
print(new_rows)

schema_file = "assets/commons/common_libraries.json"

# Проверка существования файла схемы JSON
if not os.path.isfile(schema_file):
    print(f"Файл схемы JSON '{schema_file}' не найден.")
    sys.exit(1)

# Загрузка схемы JSON
with open("assets/commons/common_libraries.json", "r") as file:
    schema = json.load(file)

# Валидация каждой новой строки
errors_found = False  # Флаг для отслеживания наличия ошибок

for idx, row in new_rows.iterrows():
    try:
        row_json = row.to_json(orient='index')
        validate(instance=json.loads(row_json), schema=schema)
        print(f"Валидация прошла успешно для строки {idx}")
    except ValidationError as e:
        errors_found = True
        print(f"Ошибка в строке {idx}, колонка '{e.path[0]}', значение '{row[e.path[0]]}': {e.message}")

# Проверка флага наличия ошибок
if errors_found:
    sys.exit(1)

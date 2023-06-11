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

# Merge the two DataFrames and create a new column '_merge' indicating where each row is from
merged = df_fork.merge(df_pr, how='outer', indicator=True)

# Check if any of the old rows have been modified or deleted
if (merged['_merge'] == 'left_only').any():
    print("\033[31mOld rows in common_libraries.tsv have been modified or deleted\033[0m")
    exit(1)

command = 'echo -n "\033[38;5;40mNo old rows have been modified or deleted in common_libraries.tsv\033[0m"'
subprocess.call(command, shell=True)

new_rows = df_pr[~df_pr.isin(df_fork)].dropna()

# Вывод содержимого new_rows
print("Содержимое new_rows:")
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
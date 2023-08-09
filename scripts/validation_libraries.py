import pandas as pd
import os
import subprocess
import json
from jsonschema import ValidationError
import sys
import re 

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

# Выше все работает правильно 

# Функция валидации
def is_valid(row, schema):

    # Проверка типа
    if 'type' in schema:
        if schema['type'] == 'string' and not isinstance(row, str):
            print(f"Ошибка в колонке {column} в строке '{row}' -> неверный тип данных. Ожидаемый тип: {schema['type']}")
            return False
        elif schema['type'] == 'integer' and not isinstance(row, int):
            print(f"Ошибка в колонке {column} в строке '{row}' -> неверный тип данных. Ожидаемый тип: {schema['type']}")
            return False

    # Проверка по паттерну
    if 'pattern' in schema and not re.match(schema['pattern'], str(row)):
        print(f"Ошибка в колонке {column} в строке '{row}' -> не соответствует ожидаемому паттерну: {schema['pattern']}")
        return False

    # Проверка по списку возможных значений
    if 'enum' in schema and row not in schema['enum']:
        print(f"Ошибка в колонке {column} в строке '{row}' -> значение не из списка возможных: {schema['enum']}")
        return False

    return True

columns_to_remove = ["publication_year", "library_concentration", "PCR_cycle_count", "read_count", "download_sizes"]
columns = new_rows.columns.drop(columns_to_remove)
new_rows = new_rows.where((pd.notna(new_rows)), None)

# Путь к папке с JSON-файлами в репозитории
schemas_path = os.path.join(os.environ["GITHUB_WORKSPACE"], 'schemas_libraries')
error_flag = False

# Итерация по списку колонок
for column in columns:
    # Поиск соответствующего JSON файла
    json_file = [file for file in os.listdir(schemas_path) if file.endswith('.json') and file.startswith(column)]

    json_file_path = os.path.join(schemas_path, json_file[0])
    with open(json_file_path, 'r') as file:
        schema = json.load(file)
    
    print(schema)

    # Применяем функцию валидации к соответствующему столбцу
    validation_results = new_rows[column].apply(is_valid, schema=schema['properties'][column])
    if not all(validation_results):
        error_flag = True
    else:
        print('Успешная валидация колонки:', column)
    print()

if error_flag:
    sys.exit(1)

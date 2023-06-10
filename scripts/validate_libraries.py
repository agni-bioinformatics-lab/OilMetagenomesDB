import os
import pandas as pd
import json
from jsonschema import validate, ValidationError

# Путь к файлу до изменения
before_file_path = os.environ["FILE_PATH_libraries"]
# Путь к файлу после изменения
after_file_path = os.environ["GITHUB_WORKSPACE"] + "/" + os.environ["FILE_PATH_libraries"]

# Загрузка данных до изменения
before_pull = pd.read_csv(before_file_path, sep="\t")

# Загрузка данных после изменения
after_pull = pd.read_csv(after_file_path, sep="\t")

print("Таблица before_pull:")
print(before_pull)
print("Таблица after_pull:")
print(after_pull)

# Находим строки, которые были добавлены
new_rows = after_pull[~after_pull.isin(before_pull)].dropna()

# Загрузка схемы JSON
with open("assets/commons/common_libraries.json", "r") as file:
    schema = json.load(file)

# Валидация каждой новой строки
for idx, row in new_rows.iterrows():
    try:
        validate(instance=row.to_dict(), schema=schema)
        print(f"Валидация прошла успешно для строки {idx}")
    except ValidationError as e:
        print(f"Ошибка в строке {idx}, колонка '{e.path[0]}', значение '{row[e.path[0]]}': {e.message}")

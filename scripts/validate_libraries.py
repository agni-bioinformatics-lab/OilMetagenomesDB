import subprocess
import os
import pandas as pd
import json
from jsonschema import validate, ValidationError

# Путь к файлу
file_path = os.environ["FILE_PATH_libraries"]

# Загрузка данных после pull request
after_pull = pd.read_csv(file_path, sep="\t")

# Получение файла до pull request
subprocess.run(["git", "fetch", "origin", "main"])
subprocess.run(["git", "checkout", "FETCH_HEAD", "--", file_path])

# Загрузка данных до pull request
before_pull = pd.read_csv(file_path, sep="\t")

# Возврат к текущей версии файла
subprocess.run(["git", "checkout", "--", file_path])

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

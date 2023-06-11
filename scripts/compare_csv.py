import pandas as pd

# Путь к первому CSV-файлу
file1_path = "comparison-results/df_pr_check.csv"

# Путь ко второму CSV-файлу
file2_path = "comparison-results/df_fork_check.csv"

# Загрузка CSV-файлов во фреймы данных
df1 = pd.read_csv(file1_path)
df2 = pd.read_csv(file2_path)

# Сравнение фреймов данных
comparison_result = df1.compare(df2)

# Вывод различий
if comparison_result.empty:
    print("CSV files are identical")
else:
    print("Differences between CSV files:")
    print(comparison_result)

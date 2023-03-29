import csv
import json

# Открываем TSV-файл для чтения
with open('crude_oil_samples.tsv', 'r') as tsvfile:
    reader = csv.DictReader(tsvfile, delimiter='\t')
    # Преобразуем данные в список словарей, приводя значения полей к нужным типам данных
    rows = [
        {
            "project_name": str(row["project_name"]),
            "publication_year": int(row["publication_year"]),
            "publication_doi": str(row["publication_doi"]),
            "site_name": str(row["site_name"]),
            "latitude": float(row["latitude"].replace(",", ".")) if isinstance(row["latitude"], str) and row["latitude"].replace(".", "", 1).isdigit() else None,
            "longitude": float(row["longitude"].replace(",", ".")) if isinstance(row["longitude"], str) and row["longitude"].replace(".", "", 1).isdigit() else None,
            "geo_loc_name": str(row["geo_loc_name"]),
            "study_primary_focus": str(row["study_primary_focus"]),
            "sequence_name": None if row["sequence_name"] == "NA" else str(row["sequence_name"]) if row["sequence_name"] != "" else raise ValueError("Empty sequence_name"),
            "depth": float(row["depth"].replace(",", ".")) if isinstance(row["depth"], str) and row["depth"].replace(".", "", 1).isdigit() else None,
            "sample_name": str(row["sample_name"]),
            "sample_age": int(row["sample_age"]) if row["sample_age"] != "NA" else None,
            "sample_age_doi": str(row["sample_age_doi"]) if row["sample_age_doi"] != "NA" else None,
            "feature": str(row["feature"]),
            "material": str(row["material"]),
            "sampling_date": int(row["sampling_date"]) if row["sampling_date"] != "NA" else None,
            "archive": str(row["archive"]),
            "archive_project": str(row["archive_project"]),
            "archive_accession": str(row["archive_accession"])
        }
        for row in reader
    ]

# Открываем JSON-файл для записи
with open('crude_oil_samples.json', 'w') as jsonfile:
    # Записываем данные в формате JSON
    json.dump(rows, jsonfile, indent=4, ensure_ascii=False)

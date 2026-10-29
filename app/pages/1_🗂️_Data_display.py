import sys
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import load_samples


def filter_column_like_geo(df, column, values):
    if values and values != "Select":
        if isinstance(values, list):
            return df[df[column].isin(values)]
        return df[df[column] == values]
    return df


def filter_column_like_depth(df, column_name, display_name=None):
    display_name = display_name or column_name

    numeric = df[column_name].replace(["None", "unknown"], np.nan).dropna().astype(float)
    min_value = numeric.min()
    max_value = numeric.max()

    if pd.isna(min_value) or pd.isna(max_value) or min_value == max_value:
        return df

    selected_values = st.sidebar.slider(
        display_name,
        float(min_value),
        float(max_value),
        (float(min_value), float(max_value)),
    )

    include_none = st.sidebar.checkbox(f"Include None in {display_name}", value=True)
    include_unknown = st.sidebar.checkbox(f"Include unknown in {display_name}", value=True)

    numeric_column = df[column_name].replace(["None", "unknown"], np.nan).astype(float)
    condition = (numeric_column >= selected_values[0]) & (numeric_column <= selected_values[1])

    if include_none:
        condition = condition | (df[column_name] == "None")
    if include_unknown:
        condition = condition | (df[column_name] == "unknown")

    return df[condition]


def filter_column_like_api(df, column_name, display_name=None):
    display_name = display_name or column_name

    numeric = pd.to_numeric(df[column_name].replace(["None", "unknown"], np.nan), errors="coerce")
    min_value = numeric.min()
    max_value = numeric.max()

    if pd.isna(min_value) or pd.isna(max_value) or min_value == max_value:
        return df

    min_value = int(min_value)
    max_value = int(max_value)
    selected_values = st.sidebar.slider(
        display_name, min_value, max_value, (min_value, max_value)
    )

    include_none = st.sidebar.checkbox(f"Include None in {display_name}", value=True)
    include_unknown = st.sidebar.checkbox(f"Include unknown in {display_name}", value=True)

    numeric_column = pd.to_numeric(df[column_name], errors="coerce")
    condition = (numeric_column >= selected_values[0]) & (numeric_column <= selected_values[1])

    if include_none:
        condition = condition | (df[column_name] == "None")
    if include_unknown:
        condition = condition | (df[column_name] == "unknown")

    return df[condition]


def sample_word(n):
    return "sample" if n == 1 else "samples"


df = load_samples().copy()

st.title("🗂️ Data display")
st.sidebar.header("Filters")

min_year = int(df["publication_year"].min())
max_year = int(df["publication_year"].max())
selected_years = st.sidebar.slider(
    "Year of publication", min_year, max_year, (min_year, max_year)
)
df = df[
    (df["publication_year"] >= selected_years[0])
    & (df["publication_year"] <= selected_years[1])
]

locations = sorted(df["geo_loc_name"].dropna().unique().tolist())
selected_locations = st.sidebar.multiselect("Country where samples were taken", locations)
df = filter_column_like_geo(df, "geo_loc_name", selected_locations)

focuses = sorted(df["study_primary_focus"].dropna().unique().tolist())
selected_focus = st.sidebar.multiselect("Focus of the research", focuses)
df = filter_column_like_geo(df, "study_primary_focus", selected_focus)

processes = sorted(df["study_process"].dropna().unique().tolist())
selected_process = st.sidebar.multiselect("Biochemical process that is studied", processes)
df = filter_column_like_geo(df, "study_process", selected_process)

df = filter_column_like_depth(df, "depth", "Sampling depth")
df = filter_column_like_depth(df, "temp", "Temperature")
df = filter_column_like_depth(df, "pH")
df = filter_column_like_depth(df, "salinity", "Salinity")
df = filter_column_like_api(df, "API", "API gravity")
df = filter_column_like_depth(df, "NO3-", "Concentration of NO₃⁻")
df = filter_column_like_depth(df, "PO43-", "Concentration of PO₄³⁻")
df = filter_column_like_depth(df, "SO42-", "Concentration of SO₄²⁻")
df = filter_column_like_depth(df, "Ca2+", "Concentration of Ca²⁺")
df = filter_column_like_depth(df, "Mg2+", "Concentration of Mg²⁺")
df = filter_column_like_depth(df, "Na+", "Concentration of Na⁺")
df = filter_column_like_depth(df, "K+", "Concentration of K⁺")
df = filter_column_like_depth(df, "Cl-", "Concentration of Cl⁻")
df = filter_column_like_depth(df, "HCO3-", "Concentration of HCO₃⁻")
df = filter_column_like_depth(df, "acetate", "Concentration of acetate")

features = sorted(df["feature"].dropna().unique().tolist())
selected_features = st.sidebar.multiselect("Medium description", features)
df = filter_column_like_geo(df, "feature", selected_features)

materials = sorted(df["material"].dropna().unique().tolist())
selected_materials = st.sidebar.multiselect("Sample type for DNA isolation", materials)
df = filter_column_like_geo(df, "material", selected_materials)

df = filter_column_like_api(df, "collection_date", "Date of sample collection")

archives = sorted(df["archive"].dropna().unique().tolist())
selected_archives = st.sidebar.multiselect("Archive of library data", archives)
df = filter_column_like_geo(df, "archive", selected_archives)

n_samples = len(df)
verb = "was" if n_samples == 1 else "were"
st.write(f"{n_samples} {sample_word(n_samples)} {verb} selected")

display = df.copy()
display["publication_year"] = display["publication_year"].astype(str)
st.dataframe(display)

st.download_button(
    label="Download data",
    data=df.to_csv(sep="\t", index=False).encode(),
    file_name="data.tsv",
    mime="text/tab-separated-values",
)

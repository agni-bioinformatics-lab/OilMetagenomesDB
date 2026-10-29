import sys
from pathlib import Path

import folium
import pandas as pd
import streamlit as st
from folium.features import CustomIcon
from streamlit_folium import st_folium

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common import MARKER_PATH, load_samples


def filter_column_like_geo(df, column, values):
    if values and values != "Select":
        if isinstance(values, list):
            return df[df[column].isin(values)]
        return df[df[column] == values]
    return df


def sample_word(n):
    return "sample" if n == 1 else "samples"


data = load_samples().copy()

st.title("🗺️ Interactive map")

numeric_depth = pd.to_numeric(data["depth"], errors="coerce")
known_depth = numeric_depth.dropna()
min_depth, max_depth = st.sidebar.slider(
    "Select the depth range",
    float(known_depth.min()),
    float(known_depth.max()),
    (float(known_depth.min()), float(known_depth.max())),
)

unique_processes = sorted(data["study_process"].dropna().unique().tolist())
selected_processes = st.sidebar.multiselect(
    "Select the research process",
    unique_processes,
    default=unique_processes,
)

if not selected_processes:
    st.warning("At least one research process must be selected. Showing all processes.")
    selected_processes = unique_processes

filtered_data = filter_column_like_geo(data, "study_process", selected_processes)
depth_values = pd.to_numeric(filtered_data["depth"], errors="coerce")
in_range = (depth_values >= min_depth) & (depth_values <= max_depth)
unknown_depth = filtered_data["depth"].isin(["unknown", "None"])
filtered_data = filtered_data[in_range | unknown_depth].copy()
filtered_data["latitude"] = pd.to_numeric(filtered_data["latitude"], errors="coerce")
filtered_data["longitude"] = pd.to_numeric(filtered_data["longitude"], errors="coerce")
filtered_data = filtered_data.dropna(subset=["latitude", "longitude"])

n_samples = len(filtered_data)
verb = "was" if n_samples == 1 else "were"
st.write(f"{n_samples} {sample_word(n_samples)} {verb} selected")

if filtered_data.empty:
    st.info("No samples with coordinates match the current filters.")
else:
    m = folium.Map(
        location=[filtered_data["latitude"].mean(), filtered_data["longitude"].mean()],
        zoom_start=2,
        tiles="http://services.arcgisonline.com/arcgis/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Esri, National Geographic",
    )

    for _, row in filtered_data.iterrows():
        popup_content = f"""
        <div>
            <strong>Archive Project:</strong> {row['archive_project']}<br>
            <a href="https://www.ncbi.nlm.nih.gov/search/all/?term={row['archive_project']}" target="_blank">NCBI Link</a>
        </div>
        """
        icon = CustomIcon(icon_image=str(MARKER_PATH), icon_size=(30, 30))
        folium.Marker(
            [row["latitude"], row["longitude"]],
            popup=folium.Popup(popup_content, max_width=300),
            icon=icon,
        ).add_to(m)

    st_folium(m, height=500, returned_objects=[])

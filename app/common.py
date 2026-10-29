from pathlib import Path

import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
REPO_ROOT = APP_DIR.parent
SAMPLES_PATH = REPO_ROOT / "common_samples" / "common_samples.tsv"
MARKER_PATH = APP_DIR / "assets" / "marker" / "oil_marker.png"
LOGO_DIR = APP_DIR / "assets" / "logo"
STYLES_PATH = APP_DIR / "styles" / "by_width.css"


@st.cache_data
def load_samples() -> pd.DataFrame:
    """Load the canonical sample table from this repository.

    keep_default_na is off so the sentinels ``None`` and ``unknown`` stay
    strings. Pandas would otherwise turn ``None`` into a missing value and
    the sidebar filters would drop those rows.
    """
    df = pd.read_csv(SAMPLES_PATH, sep="\t", keep_default_na=False)
    df["publication_year"] = pd.to_numeric(df["publication_year"], errors="coerce")
    return df

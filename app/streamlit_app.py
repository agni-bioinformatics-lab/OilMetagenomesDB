import random
import sys
from pathlib import Path

import streamlit as st
from PIL import Image
from streamlit_extras.let_it_rain import rain

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import LOGO_DIR, STYLES_PATH

emoji_list = ["🛢️", "🦠", "🧬"]
rain(
    emoji=random.choice(emoji_list),
    font_size=30,
    falling_speed=4,
    animation_length="infinite",
)


def load_css(file_name: Path) -> None:
    css = file_name.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


load_css(STYLES_PATH)

st.title("Community curated database of oil metagenomes")

st.write(
    """
    <div class="text-justify">
    Welcome to OilMetagenomesDB!

    OilMetagenomesDB is a <b>unique platform</b> designed to explore the microbial diversity of
    <b>oil fields</b> through <b>metagenomic data</b>. Through this web interface you can explore an
    interactive map of petroleum metagenomic samples, filter the sample table, and download the
    current selection. New records are added through the public GitHub repository after validation.

    This resource serves as a bridge between scientists, engineers, and anyone interested in
    <b>studying microbial communities</b> of oil fields and their <b>impact on oil production</b>.
    Through collaborative efforts and knowledge sharing, we aim to increase our understanding of
    microbial processes in oil fields and contribute to a more sustainable and efficient utilization
    of these valuable resources.
    </div>
    """,
    unsafe_allow_html=True,
)

left_col, _, center_col, _, right_col = st.columns([1, 1, 1, 1, 1])
left_col.image(Image.open(LOGO_DIR / "pish.png"), width=100)
center_col.image(Image.open(LOGO_DIR / "tatneft.png"), width=100)
right_col.image(Image.open(LOGO_DIR / "agni.png"), width=100)

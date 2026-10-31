import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SAMPLES_PATH = ROOT / "common_samples" / "common_samples.tsv"
IMAGE_PATH = ROOT / "assets" / "image" / "git_img_map.png"
README_PATH = ROOT / "README.md"

df = pd.read_csv(SAMPLES_PATH, sep="\t")
df[["latitude", "longitude"]] = df[["latitude", "longitude"]].apply(
    pd.to_numeric, errors="coerce"
)
df = df.dropna(subset=["latitude", "longitude"])
df = df[df["latitude"].between(-90, 90) & df["longitude"].between(-180, 180)]

fig, ax = plt.subplots(
    figsize=(15, 10), subplot_kw={"projection": ccrs.PlateCarree()}
)
ax.set_title("World Map with Data Points", fontsize=16)
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS, linestyle=":")
ax.add_feature(cfeature.LAND, edgecolor="black")
ax.add_feature(cfeature.LAKES, edgecolor="black")
ax.add_feature(cfeature.RIVERS)
ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
ax.scatter(
    df["longitude"],
    df["latitude"],
    s=28,
    c="#c0392b",
    marker="o",
    transform=ccrs.PlateCarree(),
    zorder=5,
)
fig.savefig(IMAGE_PATH, bbox_inches="tight", dpi=120)
plt.close(fig)

content = README_PATH.read_text(encoding="utf-8")
image_insert = "\n![My Map](./assets/image/git_img_map.png)\n"
new_content = re.sub(
    r"<!-- START-MAP-INSERT -->.*<!-- END-MAP-INSERT -->",
    f"<!-- START-MAP-INSERT -->{image_insert}<!-- END-MAP-INSERT -->",
    content,
    flags=re.DOTALL,
)
README_PATH.write_text(new_content, encoding="utf-8")

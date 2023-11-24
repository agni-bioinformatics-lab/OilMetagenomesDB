import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import re

# Read data from the URL into a DataFrame
df = pd.read_csv("https://raw.githubusercontent.com/agni-bioinformatics-lab/OilMetagenomesDB/main/common_samples/common_samples.tsv", sep="\t", decimal=".", engine='python')

# Create and save a Matplotlib plot showing the geographical distribution of the data points
fig, ax = plt.subplots(figsize=(15, 10), subplot_kw={'projection': ccrs.PlateCarree()})
ax.set_title('World Map with Data Points', fontsize=16)
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS, linestyle=':')
ax.add_feature(cfeature.LAND, edgecolor='black')
ax.add_feature(cfeature.LAKES, edgecolor='black')
ax.add_feature(cfeature.RIVERS)
ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
plt.scatter(df['longitude'], df['latitude'], s=100, c='red', marker='o', label=df['geo_loc_name'])
plt.tight_layout()
plt.savefig("assets/image/git_img_map.png", bbox_inches='tight')

# Read the README, insert the created image, and write the updated content back to the README
with open('README.md', 'r') as file:
    content = file.read()
image_insert = "\n![My Map](./assets/image/git_img_map.png)\n"
new_content = re.sub(r'<!-- START-MAP-INSERT -->.*<!-- END-MAP-INSERT -->',
                     f'<!-- START-MAP-INSERT -->{image_insert}<!-- END-MAP-INSERT -->',
                     content, flags=re.DOTALL)
with open('README.md', 'w') as file:
    file.write(new_content)
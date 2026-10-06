import sys
import numpy as np
import geopandas as gpd
import rasterio
from PIL import Image
from pyproj import Transformer
from rasterio.windows import from_bounds
from shapely.geometry import Point

URL = ("https://raw.githubusercontent.com/opengeos/maxar-open-data/master/"
       "datasets/Kahramanmaras-turkey-earthquake-23.geojson")
cid, lat, lon, size = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
gdf = gpd.read_file(URL)
row = gdf[(gdf["catalog_id"] == cid) & gdf.contains(Point(lon, lat))].iloc[0]
out = "inputs/maxar_{}_{}.tif".format(str(row["datetime"])[:10], cid)

with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"):
    with rasterio.open(row["visual"]) as src:
        crs, res = src.crs, src.res
        x, y = Transformer.from_crs("EPSG:4326", crs, always_xy=True).transform(lon, lat)
        h = size / 2
        win = from_bounds(x - h, y - h, x + h, y + h, src.transform).round_offsets().round_lengths()
        data = src.read(window=win)
        prof = src.profile.copy()
        prof.update(driver="GTiff", width=data.shape[2], height=data.shape[1],
                    transform=src.window_transform(win), compress="deflate")
        prof.pop("photometric", None)
with rasterio.open(out, "w", **prof) as dst:
    dst.write(data)
Image.fromarray(np.moveaxis(data[:3], 0, -1)).save(out.replace(".tif", ".png"))
bos = float((data[:3].sum(axis=0) == 0).mean())
print(out, "| boyut:", data.shape, "| CRS:", crs, "| GSD:", res, "| bos piksel:", round(bos, 3))

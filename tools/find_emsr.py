import glob
import os
import geopandas as gpd
import rasterio
from rasterio.warp import transform_bounds
from shapely.geometry import box

with rasterio.open("inputs/maxar_2023-02-11_10300100E19A4400.tif") as s:
    W, S, E, N = transform_bounds(s.crs, "EPSG:4326", *s.bounds)
saha = box(W, S, E, N)
print("Test penceresi (bati, guney, dogu, kuzey):", round(W, 5), round(S, 5), round(E, 5), round(N, 5))

pattern = os.path.expanduser("~/disaster-routing/data/emsr648/*/*builtUpA*.shp")
for shp in sorted(glob.glob(pattern)):
    aoi = os.path.basename(shp).split("_")[1]
    g = gpd.read_file(shp).to_crs("EPSG:4326")
    hit = g[g.intersects(saha)]
    print(aoi, "| toplam bina:", len(g), "| test penceresinde:", len(hit))
    if len(hit) > 0:
        print("   sutunlar:", list(g.columns))
        for c in g.columns:
            if "dam" in c.lower():
                print("   ", c, "->", hit[c].value_counts().to_dict())

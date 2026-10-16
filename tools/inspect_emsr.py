import glob
import os
import geopandas as gpd
import rasterio
from rasterio.warp import transform_bounds
from shapely.geometry import box

root = os.path.expanduser("~/disaster-routing/data/emsr648")
with rasterio.open("inputs/maxar_2023-02-11_10300100E19A4400.tif") as s:
    saha = box(*transform_bounds(s.crs, "EPSG:4326", *s.bounds))


def load(aoi, name):
    f = glob.glob("{}/*{}*/*{}*.shp".format(root, aoi, name))
    return gpd.read_file(f[0]).to_crs("EPSG:4326") if f else None


print("=== AOI04 imageFootprintA ===")
g = load("AOI04", "imageFootprintA")
print(g.drop(columns="geometry").to_string() if g is not None else "yok")

for ad in ["transportationL", "ancillaryCrisisInfoP"]:
    g = load("AOI04", ad)
    print("=== AOI04", ad, "===")
    if g is None:
        print("yok")
        continue
    h = g[g.intersects(saha)]
    print("toplam:", len(g), "| pencerede:", len(h), "| sutunlar:", list(g.columns))
    for c in g.columns:
        if c != "geometry" and g[c].nunique() < 15:
            print("  ", c, "->", h[c].value_counts().to_dict())

print("=== Tum AOI builtUpA hasar dagilimi ===")
for aoi in ["AOI04", "AOI16", "AOI17"]:
    g = load(aoi, "builtUpA")
    print(aoi, "| medyan alan m2:", round(g.to_crs("EPSG:32637").area.median()), "|", g["damage_gra"].value_counts().to_dict())

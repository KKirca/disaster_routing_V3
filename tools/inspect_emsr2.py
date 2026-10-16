import glob
import os
import geopandas as gpd
import rasterio
from rasterio.warp import transform_bounds
from shapely.geometry import box
from shapely.ops import unary_union

root = os.path.expanduser("~/disaster-routing/data/emsr648")
with rasterio.open("inputs/maxar_2023-02-11_10300100E19A4400.tif") as s:
    saha = box(*transform_bounds(s.crs, "EPSG:4326", *s.bounds))


def load(aoi, name):
    f = glob.glob("{}/*{}*/*{}*.shp".format(root, aoi, name))
    return gpd.read_file(f[0]).to_crs("EPSG:4326") if f else None


fp = load("AOI04", "imageFootprintA")
for tip in ["Not Analysed", "Image Footprint"]:
    u = unary_union(list(fp[fp["obj_type"] == tip].geometry))
    print("AOI04 pencerenin %{:.1f} kadari '{}' ile ortusuyor".format(100 * u.intersection(saha).area / saha.area, tip))

for aoi in ["AOI16", "AOI17"]:
    a = load(aoi, "areaOfInterestA")
    print(aoi, "AOI siniri (bati, guney, dogu, kuzey):", [round(x, 4) for x in a.total_bounds])
    b = load(aoi, "builtUpA")
    for sinif in ["Destroyed", "Damaged"]:
        h = b[b["damage_gra"] == sinif]
        c = unary_union(list(h.geometry)).centroid
        print("  ", sinif, ":", len(h), "blok | merkez (enlem, boylam):", round(c.y, 4), round(c.x, 4))

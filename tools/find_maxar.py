import sys
import geopandas as gpd
from shapely.geometry import Point

URL = ("https://raw.githubusercontent.com/opengeos/maxar-open-data/master/"
       "datasets/Kahramanmaras-turkey-earthquake-23.geojson")
lat, lon = float(sys.argv[1]), float(sys.argv[2])
gdf = gpd.read_file(URL)
print("Katalogdaki karo sayisi:", len(gdf))
print("Sutunlar:", list(gdf.columns))
hits = gdf[gdf.contains(Point(lon, lat))]
print("Noktayi iceren karo sayisi:", len(hits))
want = ["datetime", "catalog_id", "quadkey", "gsd", "view:off_nadir", "tile:data_area", "tile:clouds_percent"]
cols = [c for c in want if c in gdf.columns]
print(hits[cols].sort_values(cols[0]).to_string())

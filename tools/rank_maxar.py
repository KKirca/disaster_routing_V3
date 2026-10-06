import pandas as pd
import geopandas as gpd

URL = ("https://raw.githubusercontent.com/opengeos/maxar-open-data/master/"
       "datasets/Kahramanmaras-turkey-earthquake-23.geojson")
gdf = gpd.read_file(URL)
gdf["t"] = pd.to_datetime(gdf["datetime"], utc=True)
post = gdf[(gdf["t"] >= "2023-02-06") & (gdf["t"] <= "2023-02-15")]
post = post[post["tile:clouds_percent"] == 0]
post = post.sort_values("view:off_nadir").head(25).copy()
pt = post.geometry.representative_point()
post["enlem"], post["boylam"] = pt.y.round(4), pt.x.round(4)
cols = ["t", "catalog_id", "quadkey", "gsd", "view:off_nadir", "tile:data_area", "enlem", "boylam"]
print("6-15 Subat, bulutsuz karo sayisi:", len(gdf[(gdf["t"] >= "2023-02-06") & (gdf["t"] <= "2023-02-15")]))
print(post[cols].to_string(index=False))

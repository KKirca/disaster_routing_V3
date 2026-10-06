import numpy as np
from pyproj import Transformer
from rasterio.features import shapes
from rasterio.transform import from_bounds
from shapely.geometry import shape
from shapely.ops import transform as shp_transform


def to_utm_func(dst_crs):
    # always_xy=True: girdi (boylam, enlem) sirasinda. Olmazsa enlem/boylam yer degistirir.
    return Transformer.from_crs("EPSG:4326", dst_crs, always_xy=True).transform


def gsd_m(west, south, east, north, W, H, dst_crs):
    # Goruntunun piksel basina metre cinsinden cozunurlugu (yatay, dikey).
    f = to_utm_func(dst_crs)
    (x0, y0), (x1, y1) = f(west, south), f(east, north)
    return (x1 - x0) / W, (y1 - y0) / H


def mask_to_polygons(mask, west, south, east, north, dst_crs, min_area_m2=10.0):
    # mask: H x W bool. Donus: dst_crs (UTM, metre) cinsinden destroyed poligonlari.
    H, W = mask.shape
    T = from_bounds(west, south, east, north, W, H)  # piksel -> (boylam, enlem)
    f = to_utm_func(dst_crs)
    polys = []
    m = mask.astype(np.uint8)
    for geom, _ in shapes(m, mask=mask.astype(bool), transform=T):
        p = shp_transform(f, shape(geom))
        if p.area >= min_area_m2:
            polys.append(p)
    return polys

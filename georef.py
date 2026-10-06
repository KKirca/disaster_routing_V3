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


def mask_to_polygons_T(mask, T, src_crs, dst_crs, min_area_m2=10.0):
    # Genel surum: T = piksel -> src_crs affine donusumu. Donus: dst_crs poligonlari.
    f = Transformer.from_crs(src_crs, dst_crs, always_xy=True).transform
    polys = []
    for geom, _ in shapes(mask.astype(np.uint8), mask=mask.astype(bool), transform=T):
        p = shp_transform(f, shape(geom))
        if p.area >= min_area_m2:
            polys.append(p)
    return polys


def mask_to_polygons(mask, west, south, east, north, dst_crs, min_area_m2=10.0):
    # PNG + kose koordinatlari: affine from_bounds ile kurulur, kaynak CRS enlem/boylam.
    H, W = mask.shape
    T = from_bounds(west, south, east, north, W, H)
    return mask_to_polygons_T(mask, T, "EPSG:4326", dst_crs, min_area_m2)


from scipy import ndimage
from shapely.ops import unary_union


def detections(prob, T, src_crs, dst_crs, thr=0.5, core_thr=0.8, min_area_m2=10.0):
    # Her leke icin: poligon (dst_crs), alan, yuksek-guven cekirdek alani (m2), max olasilik.
    mask = prob > thr
    labels, n = ndimage.label(mask)
    if n == 0:
        return []
    idx = np.arange(1, n + 1)
    count = ndimage.sum(mask, labels, idx)
    core = ndimage.sum(prob > core_thr, labels, idx)
    pmax = ndimage.maximum(prob, labels, idx)
    f = Transformer.from_crs(src_crs, dst_crs, always_xy=True).transform
    out = []
    for geom, lab in shapes(labels.astype(np.int32), mask=mask, transform=T):
        i = int(lab) - 1
        p = shp_transform(f, shape(geom))
        if p.area < min_area_m2:
            continue
        px = p.area / count[i]  # bir pikselin m2 karsiligi
        out.append({"poly": p, "area": p.area, "core": core[i] * px, "pmax": float(pmax[i])})
    return out


def classify(dets, core_min=25.0, cluster_gap=10.0, cluster_n=3, cluster_area=100.0):
    # Guclu: buyuk sari cekirdek VEYA yan yana leke kumesi. Zayif: geri kalan.
    if not dets:
        return [], []
    merged = unary_union([d["poly"].buffer(cluster_gap / 2) for d in dets])
    groups = list(merged.geoms) if hasattr(merged, "geoms") else [merged]
    strong, weak = [], []
    for g in groups:
        members = [d for d in dets if d["poly"].intersects(g)]
        kume = len(members) >= cluster_n and sum(m["area"] for m in members) >= cluster_area
        for d in members:
            (strong if (d["core"] >= core_min or kume) else weak).append(d["poly"])
    return strong, weak

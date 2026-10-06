import numpy as np
from georef import mask_to_polygons, gsd_m, to_utm_func

W_, S_, E_, N_ = 36.925, 37.575, 36.940, 37.585
W, H, CRS = 1000, 800, "EPSG:32637"
gx, gy = gsd_m(W_, S_, E_, N_, W, H, CRS)
print("GSD (m/piksel): x", round(gx, 3), "| y", round(gy, 3))

mask = np.zeros((H, W), dtype=bool)
mask[400:450, 500:550] = True
mask[100:102, 100:102] = True
polys = mask_to_polygons(mask, W_, S_, E_, N_, CRS)
assert len(polys) == 1, "Beklenen 1 poligon, gelen {}".format(len(polys))
print("T7c gurultu GECTI | 2x2 kirinti atildi")

lon = W_ + 525 / W * (E_ - W_)
lat = N_ - 425 / H * (N_ - S_)
ex, ey = to_utm_func(CRS)(lon, lat)
c = polys[0].centroid
d = ((c.x - ex) ** 2 + (c.y - ey) ** 2) ** 0.5
assert d < 1.0, "Merkez sapmasi {:.2f} m".format(d)
print("T7a konum GECTI | merkez sapmasi (m):", round(d, 3))

beklenen = 50 * 50 * gx * gy
oran = polys[0].area / beklenen
assert abs(oran - 1) < 0.02, "Alan orani {:.4f}".format(oran)
print("T7b alan GECTI | alan (m2):", round(polys[0].area, 1), "| oran:", round(oran, 4))

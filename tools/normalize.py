import sys
import numpy as np
import rasterio

# KATE-CD egitim post goruntulerinden (her 10. ornek) olculen kanal istatistikleri
K_MEAN = np.array([115.2, 110.8, 99.0]).reshape(3, 1, 1)
K_STD = np.array([50.2, 48.8, 51.5]).reshape(3, 1, 1)

src_path, out_path = sys.argv[1], sys.argv[2]
with rasterio.open(src_path) as s:
    y = s.read([1, 2, 3]).astype(float)
    prof = s.profile.copy()
m = y.reshape(3, -1).mean(1).reshape(3, 1, 1)
sd = y.reshape(3, -1).std(1).reshape(3, 1, 1)
z = np.clip((y - m) / sd * K_STD + K_MEAN, 0, 255).astype(np.uint8)
prof.update(count=3, dtype="uint8")
with rasterio.open(out_path, "w", **prof) as d:
    d.write(z)
print(out_path, "| yeni ort", z.reshape(3, -1).mean(1).round(1), "| yeni std", z.reshape(3, -1).std(1).round(1))

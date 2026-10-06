import sys
import numpy as np
import rasterio
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from infer import load_model, predict_prob

pre_path, post_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
with rasterio.open(pre_path) as a, rasterio.open(post_path) as b:
    pre = np.moveaxis(a.read([1, 2, 3]), 0, -1)
    post = np.moveaxis(b.read([1, 2, 3]), 0, -1)
prob = predict_prob(load_model("checkpoints/best_model.pth", 6), np.concatenate([pre, post], axis=2))
np.save(out.replace(".png", ".npy"), prob)

print("max olasilik:", round(float(prob.max()), 3))
for t in [0.05, 0.1, 0.2, 0.3, 0.5]:
    print("olasilik > {:.2f}: piksellerin %{:.3f}".format(t, 100 * float((prob > t).mean())))

fig, ax = plt.subplots(1, 2, figsize=(20, 10))
ax[0].imshow(post)
ax[0].set_title("Sonrasi goruntu")
im = ax[1].imshow(prob, cmap="inferno", vmin=0, vmax=1)
ax[1].set_title("Olasilik haritasi (esiksiz)")
fig.colorbar(im, ax=ax[1], fraction=0.046)
for a_ in ax:
    a_.axis("off")
fig.savefig(out, dpi=70, bbox_inches="tight")
print("kaydedildi:", out)

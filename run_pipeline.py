import argparse
from pathlib import Path
import numpy as np
import rasterio
from PIL import Image
from pyproj import Transformer
from rasterio.transform import from_bounds
from rasterio.warp import transform_bounds
from infer import load_model, predict_prob
from georef import detections, classify
from routing import load_graph, close_edges_near, delay_edges_near, shortest_route, clearing_route


def load_input(image_path, bbox=None):
    # GeoTIFF: koordinat dosyadan. PNG/JPG: koordinat --bbox'tan (bati, guney, dogu, kuzey).
    if str(image_path).lower().endswith((".tif", ".tiff")):
        with rasterio.open(image_path) as src:
            img = np.moveaxis(src.read([1, 2, 3]), 0, -1)
            T, crs = src.transform, src.crs
            ll = transform_bounds(crs, "EPSG:4326", *src.bounds)
        return img, T, crs, ll
    if bbox is None:
        raise ValueError("PNG/JPG icin --bbox zorunlu")
    img = np.array(Image.open(image_path).convert("RGB"))
    H, W = img.shape[:2]
    return img, from_bounds(*bbox, W, H), "EPSG:4326", tuple(bbox)


def run(image_path, bbox, a, b, R=25.0, thr=0.5, min_area=10.0, pre_path=None):
    img, T, src_crs, ll = load_input(image_path, bbox)
    model_in = img
    if pre_path is not None:
        with rasterio.open(pre_path) as pr:
            assert pr.crs == src_crs and pr.transform == T and (pr.height, pr.width) == img.shape[:2], \
                "Oncesi ve sonrasi goruntu ayni piksel izgarasinda degil"
            pre = np.moveaxis(pr.read([1, 2, 3]), 0, -1)
        model_in = np.concatenate([pre, img], axis=2)  # egitimdeki sira: [pre, post]
    H, W = img.shape[:2]
    G = load_graph(*ll)
    crs = G.graph["crs"]
    f = Transformer.from_crs(src_crs, crs, always_xy=True).transform
    (x0, y0), (x1, y1) = f(*(T * (0, H))), f(*(T * (W, 0)))
    gx, gy = (x1 - x0) / W, (y1 - y0) / H
    print("Goruntu: {}x{} | GSD: {:.2f} x {:.2f} m/piksel".format(W, H, gx, gy))
    if abs(gx - gy) / ((gx + gy) / 2) > 0.05:
        print("UYARI: piksel kare degil ({:.2f} x {:.2f} m): kose koordinatlari ile goruntu en-boy orani uyusmuyor olabilir".format(gx, gy))
    _, L0 = shortest_route(G, a, b)
    model = load_model("checkpoints/best_model.pth", 6) if pre_path else load_model()
    prob = predict_prob(model, model_in)
    dets = detections(prob, T, src_crs, crs, thr=thr, min_area_m2=min_area)
    strong, weak = classify(dets)
    n = close_edges_near(G, strong, R=R)
    m = delay_edges_near(G, weak, R=R)
    print("Tespit: {} (guclu {}, zayif {}) | kapanan: {} | gecikmeli: {} / {} kenar".format(
        len(dets), len(strong), len(weak), n, m, len(G.edges)))
    if L0 is None:
        print("UYARI: hasar uygulanmadan once bile A-B arasi rota yok (yol agi baglantisi).")
    path, L = shortest_route(G, a, b)
    temizle = []
    if path is None:
        path, temizle = clearing_route(G, a, b)
        uz = sum(min(d["length"] for d in G[u][v].values()) for u, v in temizle)
        print("ACIK ROTA YOK. En az temizleme gerektiren rota: {} kapali segment acilmali ({:.0f} m)".format(
            len(temizle), uz))
    else:
        Lr = sum(min(d["length"] for d in G[u][v].values() if not d.get("closed", False))
                 for u, v in zip(path[:-1], path[1:]))
        print("Rota: {:.1f} m gercek uzunluk | maliyet {:.1f} | hasarsiz: {:.1f} m | uzama: +{:.1f} m".format(
            Lr, L, L0, Lr - L0))
    return img, prob, G, path, T, src_crs, temizle


def draw(img, prob, G, path, T, src_crs, out_path, thr=0.5, temizle=()):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    H, W = img.shape[:2]
    back = Transformer.from_crs(G.graph["crs"], src_crs, always_xy=True).transform
    inv = ~T  # affine'in tersi: kaynak CRS -> piksel

    def px(x, y):
        return inv * back(x, y)

    fig, ax = plt.subplots(figsize=(10, 10 * H / W))
    ax.imshow(img)
    ax.imshow(np.ma.masked_where(prob <= thr, prob), cmap="autumn", alpha=0.5)
    for u, v, d in G.edges(data=True):
        if "geometry" in d:
            coords = list(d["geometry"].coords)
        else:
            coords = [(G.nodes[u]["x"], G.nodes[u]["y"]), (G.nodes[v]["x"], G.nodes[v]["y"])]
        xs, ys = zip(*[px(x, y) for x, y in coords])
        if d.get("closed", False):
            renk, kal = "red", 1.8
        elif d.get("delay", 0) > 0:
            renk, kal = "orange", 1.4
        else:
            renk, kal = "white", 0.6
        ax.plot(xs, ys, color=renk, lw=kal, alpha=0.8)
    if path:
        xs, ys = zip(*[px(G.nodes[n]["x"], G.nodes[n]["y"]) for n in path])
        ax.plot(xs, ys, color="cyan", lw=3)
    for u, v in temizle:
        xs, ys = zip(*[px(G.nodes[n]["x"], G.nodes[n]["y"]) for n in (u, v)])
        ax.plot(xs, ys, color="magenta", lw=6)
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")
    fig.savefig(out_path, dpi=150, bbox_inches="tight")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--image", required=True)
    p.add_argument("--bbox", nargs=4, type=float, default=None, metavar=("BATI", "GUNEY", "DOGU", "KUZEY"),
                   help="Sadece PNG/JPG icin. GeoTIFF koordinati kendi icinde tasir.")
    p.add_argument("--a", nargs=2, type=float, required=True, metavar=("ENLEM", "BOYLAM"))
    p.add_argument("--b", nargs=2, type=float, required=True, metavar=("ENLEM", "BOYLAM"))
    p.add_argument("--R", type=float, default=25.0)
    p.add_argument("--thr", type=float, default=0.5)
    p.add_argument("--min-area", type=float, default=10.0)
    p.add_argument("--pre", default=None, help="Deprem oncesi GeoTIFF: verilirse 6 kanal model kullanilir")
    p.add_argument("--out", default="outputs/rota.png")
    args = p.parse_args()
    img, prob, G, path, T, src_crs, temizle = run(args.image, args.bbox, tuple(args.a), tuple(args.b),
                                         args.R, args.thr, args.min_area, args.pre)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    draw(img, prob, G, path, T, src_crs, args.out, args.thr, temizle)
    print("Gorsel:", args.out)

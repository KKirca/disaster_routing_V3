import argparse
from pathlib import Path
import numpy as np
from PIL import Image
from infer import load_model, predict_prob
from georef import mask_to_polygons, gsd_m
from routing import load_graph, close_edges_near, shortest_route


def run(image_path, bbox, a, b, R=25.0, thr=0.5, min_area=10.0):
    W_, S_, E_, N_ = bbox
    img = np.array(Image.open(image_path).convert("RGB"))
    H, W = img.shape[:2]
    G = load_graph(W_, S_, E_, N_)
    crs = G.graph["crs"]
    gx, gy = gsd_m(W_, S_, E_, N_, W, H, crs)
    print("Goruntu: {}x{} | GSD: {:.2f} x {:.2f} m/piksel".format(W, H, gx, gy))
    if abs(gx - gy) / ((gx + gy) / 2) > 0.05:
        print("UYARI: piksel kare degil ({:.2f} x {:.2f} m): kose koordinatlari ile goruntu en-boy orani uyusmuyor olabilir".format(gx, gy))
    _, L0 = shortest_route(G, a, b)
    prob = predict_prob(load_model(), img)
    polys = mask_to_polygons(prob > thr, W_, S_, E_, N_, crs, min_area_m2=min_area)
    n = close_edges_near(G, polys, R=R)
    print("Destroyed poligon: {} | kapanan kenar: {} / {}".format(len(polys), n, len(G.edges)))
    path, L = shortest_route(G, a, b)
    if path is None:
        print("ROTA YOK: A ile B arasindaki tum yollar kapali.")
    else:
        print("Rota: {:.1f} m | hasarsiz: {:.1f} m | fark: +{:.1f} m".format(L, L0, L - L0))
    return img, prob, G, path


def draw(img, prob, G, path, bbox, out_path, thr=0.5):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from pyproj import Transformer
    W_, S_, E_, N_ = bbox
    H, W = img.shape[:2]
    back = Transformer.from_crs(G.graph["crs"], "EPSG:4326", always_xy=True).transform

    def px(x, y):
        lon, lat = back(x, y)
        return (lon - W_) / (E_ - W_) * W, (N_ - lat) / (N_ - S_) * H

    fig, ax = plt.subplots(figsize=(10, 10 * H / W))
    ax.imshow(img)
    ax.imshow(np.ma.masked_where(prob <= thr, prob), cmap="autumn", alpha=0.5)
    for u, v, d in G.edges(data=True):
        if "geometry" in d:
            coords = list(d["geometry"].coords)
        else:
            coords = [(G.nodes[u]["x"], G.nodes[u]["y"]), (G.nodes[v]["x"], G.nodes[v]["y"])]
        xs, ys = zip(*[px(x, y) for x, y in coords])
        kapali = d.get("closed", False)
        ax.plot(xs, ys, color="red" if kapali else "white", lw=1.8 if kapali else 0.6, alpha=0.8)
    if path:
        xs, ys = zip(*[px(G.nodes[n]["x"], G.nodes[n]["y"]) for n in path])
        ax.plot(xs, ys, color="cyan", lw=3)
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")
    fig.savefig(out_path, dpi=150, bbox_inches="tight")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--image", required=True)
    p.add_argument("--bbox", nargs=4, type=float, required=True, metavar=("BATI", "GUNEY", "DOGU", "KUZEY"))
    p.add_argument("--a", nargs=2, type=float, required=True, metavar=("ENLEM", "BOYLAM"))
    p.add_argument("--b", nargs=2, type=float, required=True, metavar=("ENLEM", "BOYLAM"))
    p.add_argument("--R", type=float, default=25.0)
    p.add_argument("--thr", type=float, default=0.5)
    p.add_argument("--min-area", type=float, default=10.0)
    p.add_argument("--out", default="outputs/rota.png")
    args = p.parse_args()
    bbox = tuple(args.bbox)
    img, prob, G, path = run(args.image, bbox, tuple(args.a), tuple(args.b), args.R, args.thr, args.min_area)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    draw(img, prob, G, path, bbox, args.out, args.thr)
    print("Gorsel:", args.out)

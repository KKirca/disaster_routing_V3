import glob
import os
import sys
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import osmnx as ox
from routing import load_graph, shortest_route, clearing_route, close_edges_near, delay_edges_near

AOI = sys.argv[1] if len(sys.argv) > 1 else "AOI17"
root = os.path.expanduser("~/disaster-routing/data/emsr648")


def load(name):
    f = glob.glob("{}/*{}*/*{}*.shp".format(root, AOI, name))
    return gpd.read_file(f[0]).to_crs("EPSG:4326")


W, S, E, N = load("areaOfInterestA").total_bounds
A = (S + 0.15 * (N - S), W + 0.15 * (E - W))
B = (N - 0.15 * (N - S), E - 0.15 * (E - W))
print(AOI, "| A (enlem, boylam):", [round(x, 5) for x in A], "| B:", [round(x, 5) for x in B])
G0 = load_graph(W, S, E, N)
crs = G0.graph["crs"]
blocks = load("builtUpA").to_crs(crs)
print("Dugum:", len(G0.nodes), "| kenar:", len(G0.edges), "| blok:", len(blocks))
print(blocks["damage_gra"].value_counts().to_dict())


def grup(sinif):
    return list(blocks[blocks["damage_gra"] == sinif].geometry)


def gercek(G, path):
    top = 0.0
    for u, v in zip(path[:-1], path[1:]):
        acik = [d["length"] for d in G[u][v].values() if not d.get("closed", False)]
        top += min(acik) if acik else min(d["length"] for d in G[u][v].values())
    return top


def uygula(R):
    G = G0.copy()
    close_edges_near(G, grup("Destroyed"), R=R)
    delay_edges_near(G, grup("Damaged"), R=R, penalty=100.0)
    delay_edges_near(G, grup("Possibly damaged"), R=R, penalty=50.0)
    kapali = sum(1 for _, _, d in G.edges(data=True) if d.get("closed", False))
    gec = sum(1 for _, _, d in G.edges(data=True) if d.get("delay", 0) > 0 and not d.get("closed", False))
    path, L = shortest_route(G, A, B)
    temizle = []
    if path is None:
        path, temizle = clearing_route(G, A, B)
    return G, path, temizle, kapali, gec


p0, L0 = shortest_route(G0, A, B)
print("Hasarsiz rota:", "YOK" if p0 is None else "{:.0f} m".format(L0))
sonuc = {}
satirlar = ["R_m,kapali_kenar,gecikmeli_kenar,rota_durumu,gercek_uzunluk_m,uzama_m,temizlenecek_segment"]
for R in [10, 25, 40]:
    G, path, temizle, kapali, gec = uygula(R)
    uz = gercek(G, path)
    durum = "ACIK" if not temizle else "TEMIZLEME GEREKLI"
    satirlar.append("{},{},{},{},{:.0f},{:.0f},{}".format(R, kapali, gec, durum, uz, uz - (L0 or 0), len(temizle)))
    sonuc[R] = (G, path, temizle)
os.makedirs("outputs", exist_ok=True)
open("outputs/emsr_{}_duyarlilik.csv".format(AOI), "w").write("\n".join(satirlar) + "\n")
print("\n".join(satirlar))


G, path, temizle = sonuc[25]
e = ox.graph_to_gdfs(G, nodes=False)
kap = e["closed"].fillna(False).astype(bool) if "closed" in e.columns else e["length"] < 0
gec = (e["delay"].fillna(0) > 0) & ~kap if "delay" in e.columns else kap
fig, ax = plt.subplots(figsize=(11, 11))
for sinif, renk in [("No visible damage", "#dddddd"), ("Possibly damaged", "#fff3a0"),
                    ("Damaged", "#ffd08a"), ("Destroyed", "#ff9090")]:
    alt = blocks[blocks["damage_gra"] == sinif]
    if len(alt):
        alt.plot(ax=ax, color=renk, edgecolor="none")
e[~kap & ~gec].plot(ax=ax, color="gray", linewidth=0.6)
e[gec].plot(ax=ax, color="orange", linewidth=1.4)
e[kap].plot(ax=ax, color="red", linewidth=1.8)
xs = [G.nodes[n]["x"] for n in path]
ys = [G.nodes[n]["y"] for n in path]
ax.plot(xs, ys, color="blue", linewidth=3)
ax.set_title("{} | R=25 m | mavi: rota | kirmizi: kapali | turuncu: gecikmeli".format(AOI))
ax.axis("off")
fig.savefig("outputs/emsr_{}_R25.png".format(AOI), dpi=80, bbox_inches="tight")
print("kaydedildi: outputs/emsr_{}_R25.png".format(AOI))

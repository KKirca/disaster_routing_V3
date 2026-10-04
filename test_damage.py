import osmnx as ox
from shapely.geometry import Point
from routing import load_graph, shortest_route, edge_cost, close_edges_near

G = load_graph(36.925, 37.575, 36.940, 37.585)
A, B = (37.577, 36.927), (37.583, 36.938)
path, L = shortest_route(G, A, B)
uses_closed = lambda p: any(edge_cost(u, v, G[u][v]) is None for u, v in zip(p[:-1], p[1:]))

n = close_edges_near(G, [Point(0, 0).buffer(5)], R=25)
assert n == 0, "Uzaktaki poligon {} kenar kapatti".format(n)
print("T5 negatif kontrol GECTI | uzak poligon -> 0 kenar")

u, v = path[len(path) // 2], path[len(path) // 2 + 1]
edges = ox.graph_to_gdfs(G, nodes=False)
bina = edges.loc[(u, v, 0), "geometry"].interpolate(0.5, normalized=True).buffer(5)
n = close_edges_near(G, [bina], R=25)
assert n >= 1 and uses_closed(path), "Yol ortasindaki bina kenari kapatmadi"
path2, L2 = shortest_route(G, A, B)
assert path2 is not None and not uses_closed(path2), "Yeni rota kapali yoldan geciyor"
print("T4 hasar GECTI | kapanan kenar:", n, "| eski:", round(L, 1), "m | yeni:", round(L2, 1), "m")

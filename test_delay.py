import osmnx as ox
from routing import load_graph, shortest_route, edge_cost, delay_edges_near

G = load_graph(36.925, 37.575, 36.940, 37.585)
A, B = (37.577, 36.927), (37.583, 36.938)
path, L = shortest_route(G, A, B)

u, v = path[len(path) // 2], path[len(path) // 2 + 1]
edges = ox.graph_to_gdfs(G, nodes=False)
leke = edges.loc[(u, v, 0), "geometry"].interpolate(0.5, normalized=True).buffer(5)
m = delay_edges_near(G, [leke], R=25, penalty=100)
eski_yeni_maliyet = sum(edge_cost(a, b, G[a][b]) for a, b in zip(path[:-1], path[1:]))
path2, L2 = shortest_route(G, A, B)
assert m >= 1 and path2 is not None
assert L2 <= eski_yeni_maliyet + 1e-6, "A* eski rotadan pahali bir rota secti"
print("T8a gecikme GECTI | gecikmeli kenar:", m, "| eski rota yeni maliyet:", round(eski_yeni_maliyet, 1), "| secilen:", round(L2, 1))

for a, b, d in G.edges(data=True):
    d["delay"] = d.get("delay", 0.0) + 1000.0
assert shortest_route(G, A, B)[0] is not None, "Gecikme izolasyon uretti"
print("T8b gecikme izolasyon uretmez GECTI")

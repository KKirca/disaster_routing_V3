from routing import load_graph, shortest_route, clearing_route, edge_cost

G = load_graph(36.925, 37.575, 36.940, 37.585)
A, B = (37.577, 36.927), (37.583, 36.938)
for u, v, d in G.edges(data=True):
    d["closed"] = True
assert shortest_route(G, A, B) == (None, None)
path, temizle = clearing_route(G, A, B)
assert path is not None and len(temizle) == len(path) - 1, "Tum yollar kapaliyken her adim temizlenmeli"
assert all(edge_cost(u, v, G[u][v]) is None for u, v in temizle), "Acik bir yol temizleme listesine girdi"
print("T9 temizleme rotasi GECTI | temizlenecek segment:", len(temizle))

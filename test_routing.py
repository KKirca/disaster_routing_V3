import networkx as nx
from routing import load_graph, shortest_route, edge_cost

G = load_graph(36.925, 37.575, 36.940, 37.585)
A, B = (37.577, 36.927), (37.583, 36.938)

path, L = shortest_route(G, A, B)
assert path is not None, "Kapali kenar yokken rota bulunamadi"
L_dijkstra = nx.dijkstra_path_length(G, path[0], path[-1], weight=edge_cost)
assert abs(L - L_dijkstra) < 1e-6, "A* ve Dijkstra farkli: {} vs {}".format(L, L_dijkstra)
print("T1 negatif kontrol GECTI | dugum:", len(path), "| uzunluk (m):", round(L, 1))


def close_road(G, u, v):
    # Enkaz yolu iki yonde de tikar: u->v ve v->u'daki tum paralel kenarlar.
    for a, b in ((u, v), (v, u)):
        if G.has_edge(a, b):
            for d in G[a][b].values():
                d["closed"] = True


def uses_closed(G, path):
    # Rotadaki herhangi bir adimda acik paralel kenar kalmamissa rota kapali yol kullaniyor.
    return any(edge_cost(u, v, G[u][v]) is None for u, v in zip(path[:-1], path[1:]))


mid = len(path) // 2
close_road(G, path[mid], path[mid + 1])
assert uses_closed(G, path), "Oz-test: kontrol fonksiyonu kapali yolu yakalayamadi"
path2, L2 = shortest_route(G, A, B)
assert path2 is not None, "Tek yol kapatilinca rota kayboldu"
assert not uses_closed(G, path2), "Yeni rota kapali yoldan geciyor"
assert L2 >= L - 1e-6, "Kenar kapatinca rota kisaldi: {} < {}".format(L2, L)
print("T2 sapma GECTI | eski:", round(L, 1), "m | yeni:", round(L2, 1), "m | fark: +", round(L2 - L, 1), "m")

for u, v, d in G.edges(data=True):
    d["closed"] = True
assert shortest_route(G, A, B) == (None, None), "Tum yollar kapaliyken rota bulundu"
print("T3 izolasyon GECTI | tum yollar kapali -> rota yok")

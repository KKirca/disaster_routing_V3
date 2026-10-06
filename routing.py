import osmnx as ox
import networkx as nx


def load_graph(west, south, east, north):
    # OSMnx 2.x bbox sirasi: (bati, guney, dogu, kuzey)
    G = ox.graph_from_bbox((west, south, east, north), network_type="drive")
    # Enlem/boylam (derece) -> UTM (metre). Tum mesafe islemleri metrede yapilir.
    G = ox.project_graph(G)
    # Kirpma ve tek yonlu sokaklar kopuk adaciklar yaratir: sadece en buyuk guclu bagli bileseni tut.
    return ox.truncate.largest_component(G, strongly=True)

from shapely.geometry import Point


def nearest_node(G, lat, lon):
    # A/B enlem/boylam gelir; grafla ayni CRS'e (UTM) cevrilir, en yakin kavsak bulunur.
    pt, _ = ox.projection.project_geometry(Point(lon, lat), to_crs=G.graph["crs"])
    return ox.distance.nearest_nodes(G, X=pt.x, Y=pt.y)


def edge_cost(u, v, data):
    # MultiDiGraph: data = {anahtar: ozellikler}, ayni iki dugum arasindaki paralel kenarlar.
    # Kapali olmayanlarin en kisasi; hepsi kapaliysa None -> A* kenari yok sayar.
    lengths = [d["length"] + d.get("delay", 0.0) for d in data.values() if not d.get("closed", False)]
    return min(lengths) if lengths else None


def shortest_route(G, a_latlon, b_latlon):
    src = nearest_node(G, *a_latlon)
    dst = nearest_node(G, *b_latlon)

    def h(n1, n2):
        # Duz cizgi mesafesi (metre): hicbir yol bundan kisa olamaz -> admissible.
        dx = G.nodes[n1]["x"] - G.nodes[n2]["x"]
        dy = G.nodes[n1]["y"] - G.nodes[n2]["y"]
        return (dx * dx + dy * dy) ** 0.5

    try:
        path = nx.astar_path(G, src, dst, heuristic=h, weight=edge_cost)
    except nx.NetworkXNoPath:
        return None, None
    length = sum(edge_cost(u, v, G[u][v]) for u, v in zip(path[:-1], path[1:]))
    return path, length


from shapely.ops import unary_union


def close_edges_near(G, polygons, R=25.0):
    # polygons: grafla ayni CRS'te (UTM, metre) destroyed bina poligonlari.
    # Kenar geometrisine R metreden yakin poligon varsa kenar kapanir.
    # mesafe(kenar, poligon) <= R  <=>  kenar, R kadar genisletilmis poligonla kesisir.
    if not polygons:
        return 0
    danger = unary_union([p.buffer(R) for p in polygons])
    edges = ox.graph_to_gdfs(G, nodes=False)
    hit = edges.index[edges.intersects(danger)]
    for u, v, k in hit:
        G[u][v][k]["closed"] = True
    return len(hit)


def delay_edges_near(G, polygons, R=25.0, penalty=100.0):
    # Zayif tespit: kenari kapatmaz, yakindaki her leke icin 'penalty' metre esdeger gecikme ekler.
    if not polygons:
        return 0
    edges = ox.graph_to_gdfs(G, nodes=False)
    etkilenen = set()
    for poly in polygons:
        for i in edges.sindex.query(poly.buffer(R), predicate="intersects"):
            u, v, k = edges.index[i]
            G[u][v][k]["delay"] = G[u][v][k].get("delay", 0.0) + penalty
            etkilenen.add((u, v, k))
    return len(etkilenen)


def clearing_route(G, a_latlon, b_latlon, clear_penalty=5000.0):
    # Acik rota yoksa: kapali kenarlar cok pahali ama gecilebilir sayilir.
    # Donus: rota ve temizlenmesi gereken kapali kenarlar.
    src = nearest_node(G, *a_latlon)
    dst = nearest_node(G, *b_latlon)

    def cost(u, v, data):
        return min(d["length"] + d.get("delay", 0.0) + (clear_penalty if d.get("closed", False) else 0.0)
                   for d in data.values())

    def h(n1, n2):
        dx = G.nodes[n1]["x"] - G.nodes[n2]["x"]
        dy = G.nodes[n1]["y"] - G.nodes[n2]["y"]
        return (dx * dx + dy * dy) ** 0.5

    path = nx.astar_path(G, src, dst, heuristic=h, weight=cost)
    temizle = [(u, v) for u, v in zip(path[:-1], path[1:]) if edge_cost(u, v, G[u][v]) is None]
    return path, temizle

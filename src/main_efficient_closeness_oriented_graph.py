from utils.graph_utils import get_oriented_city_graph, plot_city_graph
from efficient_closeness.top_k_closeness import top_k_closeness

cities = [
    "Paris, France",
    "Lyon, France",
    "Marseille, France",
    "Toulouse, France",
    "Bordeaux, France",
    "Nice, France",
    "Nantes, France",
    "Dijon, France",
    "Reims, France",
    "Annecy, France"
]

k = 5

for city in cities:
    G = get_oriented_city_graph(city)
    A = top_k_closeness(G, k)

    topk_sorted = sorted(A.items(), key=lambda x: x[1], reverse=True)[:k]
    top_nodes = [n for n, _ in topk_sorted]

    plot_city_graph(G, city, top_nodes=top_nodes, mode="efficient_oriented")

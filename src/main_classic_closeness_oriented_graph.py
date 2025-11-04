from utils.graph_utils import get_oriented_city_graph, plot_city_graph
from classic_closeness.classic_closeness import closeness_centrality_all_nodes

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

for city in cities:
    G = get_oriented_city_graph(city)
    closeness = closeness_centrality_all_nodes(G)
    top5 = sorted(closeness, key=closeness.get, reverse=True)[:5]
    plot_city_graph(G, city, top_nodes=top5, mode="classic_oriented")

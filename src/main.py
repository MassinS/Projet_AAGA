"""
/// pour tester au départ le classic_closeness.py si ça marche bien 


import networkx as nx
from classic_closeness import closeness_centrality_all_nodes  # ton fichier précédent

if __name__ == "__main__":
    # Création d’un petit graphe pour tester
    G = nx.Graph()
    G.add_edges_from([
        ('A', 'B'),
        ('A', 'C'),
        ('B', 'D'),
        ('C', 'D'),
        ('D', 'E')
    ])
    
    result = closeness_centrality_all_nodes(G)
    print("Closeness centrality for all nodes:")
    for node, cc in result.items():
        print(f"{node}: {cc:.4f}") """
        
        
from graph_utils import get_city_graph, plot_city_graph
from classic_closeness import closeness_centrality_all_nodes

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
    G = get_city_graph(city)
    closeness = closeness_centrality_all_nodes(G)
    top5 = sorted(closeness, key=closeness.get, reverse=True)[:5]
    plot_city_graph(G, city, top_nodes=top5)

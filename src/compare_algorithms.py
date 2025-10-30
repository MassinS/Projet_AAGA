import time
import networkx as nx
from graph_utils import get_city_graph, get_oriented_city_graph
from classic_closeness import closeness_centrality_all_nodes
from efficient_closeness import top_k_closeness
import os

def compare_top5(city):
    print(f"\n🧭 Testing city: {city}")
    G = get_oriented_city_graph(city)
    # Charger le graphe
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(BASE_DIR, "..", "data", "Wiki-Vote.txt")
    Gprime = nx.read_edgelist(path,create_using=nx.DiGraph(),nodetype=int)

    print(f"Graph loaded: {len(G.nodes())} nodes, {len(G.edges())} edges")
    print("Is strongly connected?", nx.is_strongly_connected(G))
    print("Number of connected components:", nx.number_connected_components(G.to_undirected()))

    # --- Classic closeness ---
    start_classic = time.perf_counter()
    classic = closeness_centrality_all_nodes(G)
    end_classic = time.perf_counter()
    top5_classic = sorted(classic, key=classic.get, reverse=True)[:5]
    print(f"Classic  Top5: {top5_classic}")
    print(f"Classic  Time: {end_classic - start_classic:.4f} seconds")

    # --- SUNYA top-k version ---
    start_optimized = time.perf_counter()
    optimized = top_k_closeness.top_k_closeness(G, 5)
    end_optimized = time.perf_counter()
    print(f"Optimized Time: {end_optimized - start_optimized:.4f} seconds")
    print(f"Optimized Top5: {optimized}")

    # --- Compare ---
    intersection = set(top5_classic) & set(optimized)
    overlap = len(intersection) / 5 * 100

    
    
    print(f"Overlap: {overlap:.1f}%  ({intersection})")

    return overlap

# --- Test sur plusieurs villes ---
cities = [
    "Paris, France",
    "Lyon, France",
    "Marseille, France",
    "Toulouse, France",
    "Bordeaux, France",
    "Nice, France"
]

overlaps = []
for city in cities:
    overlaps.append(compare_top5(city))

print("\n🔎 Résumé global :")
print(f"Moyenne du recouvrement des Top5 : {sum(overlaps)/len(overlaps):.2f}%")

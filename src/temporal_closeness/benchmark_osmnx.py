# ============================================================
# benchmark_osmnx_algo2_full.py — Algo 2 sur graphes complets
# ============================================================

import os
import time
import random
import csv
import osmnx as ox
import networkx as nx

from temporal_graph import TemporalGraph
from topk_temporal_closeness import topk_temporal_closeness


def osmnx_to_temporal_graph(G_osmnx, T_max=100, lambda_max=10, seed=None):
    """
    Convertit un graphe OSMnx en graphe temporel (u, v, t, λ)
    avec t un temps aléatoire et λ une durée proportionnelle à la longueur.
    """
    if seed is not None:
        random.seed(seed)
    G_temp = TemporalGraph()
    for u, v, data in G_osmnx.edges(data=True):
        if u == v:
            continue
        l = min(lambda_max, max(1, int(data.get("length", 50) / 100)))
        t = random.randint(0, T_max - l)
        G_temp.add_edge(str(u), str(v), t, l)
    return G_temp


def get_largest_strongly_connected_component(G):
    """
    Récupère la plus grande composante fortement (ou simplement) connexe.
    """
    if G.is_directed():
        comps = list(nx.strongly_connected_components(G))
        largest = max(comps, key=len)
        return G.subgraph(largest).copy()
    else:
        comps = list(nx.connected_components(G))
        largest = max(comps, key=len)
        return G.subgraph(largest).copy()


def benchmark_city(city, k=5, T_max=100, interval=(0, 100)):
    """
    Exécute le benchmark de l’Algorithme 2 (Top-k Temporal Closeness)
    sur le graphe complet de la ville.
    """
    print(f"\n🏙️  {city}")
    try:
        # Chargement du graphe routier complet de la ville
        G_static = ox.graph_from_place(city, network_type="drive")

        # Extraction de la composante fortement connexe principale
        G_static = get_largest_strongly_connected_component(G_static)
        num_nodes = len(G_static.nodes())
        num_edges = len(G_static.edges())

        print(f"   📊 Graphe complet : {num_nodes} nœuds, {num_edges} arêtes")

        # Conversion en graphe temporel
        G_temp = osmnx_to_temporal_graph(G_static, T_max=T_max, lambda_max=5, seed=42)

        # Exécution de l’Algorithme 2
        print("   🔍 Calcul avec l’Algorithme 2 (Top-k Temporal Closeness)...")
        start = time.perf_counter()
        topk_temporal_closeness(G_temp, k=k, interval=interval)
        t_algo2 = time.perf_counter() - start

        print(f"⏱️  Temps Algo 2 = {t_algo2:.3f} s")

        return {
            "city": city,
            "nodes": num_nodes,
            "edges": num_edges,
            "k": k,
            "algo2_time_s": round(t_algo2, 6),
        }

    except Exception as e:
        print(f"⚠️  Erreur sur {city} : {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    cities = [
        "Rennes, France",
        "Nantes, France",
        "5th arrondissement, Paris, France",
        "7th arrondissement, Lyon, France",
        "1st arrondissement, Marseille, France",
        "Lille, France",
    ]

    results = []
    os.makedirs("results", exist_ok=True)
    csv_path = os.path.join("results", "results_osmnx_algo2_full.csv")

    print("=== 🧭 Benchmark Algo 2 — Top-k Temporal Closeness sur graphes complets ===")

    for city in cities:
        print(f"\n{'=' * 60}")
        result = benchmark_city(city, k=3)
        if result:
            results.append(result)
        print(f"{'=' * 60}")

    # Sauvegarde des résultats
    if results:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["city", "nodes", "edges", "k", "algo2_time_s"])
            writer.writeheader()
            writer.writerows(results)

        print(f"\n✅ Résultats enregistrés dans : {csv_path}")
        print(f"📊 {len(results)} villes traitées avec succès")
    else:
        print("❌ Aucun résultat à enregistrer")

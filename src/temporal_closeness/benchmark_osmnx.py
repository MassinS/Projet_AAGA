# ============================================================
# benchmark_osmnx_algo2_full.py — Algo 2 + Visualisation Top-k
# ============================================================

import os
import time
import random
import csv
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt

from temporal_graph import TemporalGraph
from topk_temporal_closeness import topk_temporal_closeness


# ------------------------------------------------------------
# Conversion OSMnx → Graphe temporel
# ------------------------------------------------------------
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
        G_temp.add_edge(u, v, t, l)
    return G_temp


# ------------------------------------------------------------
# Extraction de la plus grande composante connexe
# ------------------------------------------------------------
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


# ------------------------------------------------------------
# Visualisation des Top-k sur le graphe routier
# ------------------------------------------------------------
def plot_topk_on_city(G_static, topk_nodes, city, save_dir="graph/temporel"):
    """
    Affiche le graphe routier d'une ville avec les Top-k sommets mis en évidence.
    - G_static : graphe OSMnx (statique)
    - topk_nodes : liste des identifiants de nœuds à surligner
    - city : nom de la ville (pour le titre et le nom du fichier)
    """
    fig, ax = ox.plot_graph(
        G_static,
        node_size=0,
        edge_color="white",
        bgcolor="black",
        show=False,
        close=False
    )

    # ✅ Affiche les coordonnées des nœuds top-k
    node_x = [G_static.nodes[n]["x"] for n in topk_nodes if n in G_static.nodes]
    node_y = [G_static.nodes[n]["y"] for n in topk_nodes if n in G_static.nodes]

    if len(node_x) == 0:
        print("⚠️  Aucun nœud top-k trouvé dans le graphe statique ! (vérifie les IDs)")
    else:
        ax.scatter(node_x, node_y, c="red", s=50, label="Top closeness", zorder=3)
        for i, (x, y) in enumerate(zip(node_x, node_y)):
            ax.text(x, y, f"{i+1}", color="white", fontsize=6, zorder=4)

    ax.legend(facecolor="black", edgecolor="white", labelcolor="white")
    ax.set_title(f"Graphe routier de {city}", color="white")

    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, f"{city.replace(',', '').replace(' ', '_')}_graph.png")
    plt.savefig(path, dpi=300, bbox_inches="tight", facecolor="black")
    plt.close(fig)

    print(f"🖼️  Graphe sauvegardé dans : {path}")


# ------------------------------------------------------------
# Benchmark principal pour une ville
# ------------------------------------------------------------
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
        result_topk = topk_temporal_closeness(G_temp, k=k, interval=interval)
        t_algo2 = time.perf_counter() - start

        print(f"⏱️  Temps Algo 2 = {t_algo2:.3f} s")

        # 5️⃣ Extraire les IDs des top-k noeuds
        topk_nodes = [node for _, node in result_topk]
        print(f"   🔺 Nœuds top-{k} : {topk_nodes}")

        # 6️⃣ Visualisation
        plot_topk_on_city(G_static, topk_nodes, city)

        # 7️⃣ Retourner les résultats
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


# ------------------------------------------------------------
# Point d'entrée principal
# ------------------------------------------------------------
if __name__ == "__main__":
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

    results = []
    os.makedirs("results", exist_ok=True)
    csv_path = os.path.join("results", "results_osmnx_algo2_full.csv")

    print("=== 🧭 Benchmark Algo 2 — Top-k Temporal Closeness sur graphes complets ===")

    for city in cities:
        result = benchmark_city(city, k=5)
        if result:
            results.append(result)
        print(f"{'=' * 60}")

    # Sauvegarde CSV
    if results:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["city", "nodes", "edges", "k", "algo2_time_s"])
            writer.writeheader()
            writer.writerows(results)

        print(f"\n✅ Résultats enregistrés dans : {csv_path}")
        print(f"📊 {len(results)} villes traitées avec succès")
    else:
        print("❌ Aucun résultat à enregistrer")

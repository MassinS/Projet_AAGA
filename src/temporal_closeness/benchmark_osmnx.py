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
def get_largest_component(G):
    """
    Récupère la plus grande composante fortement (ou simplement) connexe.
    """
    if G.is_directed():
        comps = list(nx.strongly_connected_components(G))
    else:
        comps = list(nx.connected_components(G))
    largest = max(comps, key=len)
    return G.subgraph(largest).copy()


# ------------------------------------------------------------
# Visualisation des Top-k sur le graphe routier
# ------------------------------------------------------------
def plot_topk_on_city(G_static, topk_nodes, city, save_dir, oriented):
    """
    Affiche le graphe routier d'une ville avec les Top-k sommets mis en évidence.
    - G_static : graphe OSMnx (statique)
    - topk_nodes : liste des identifiants de nœuds à surligner
    - city : nom de la ville (pour le titre et le nom du fichier)
    - save_dir : dossier où sauvegarder l’image
    - oriented : booléen, True si graphe orienté
    """
    fig, ax = ox.plot_graph(
        G_static,
        node_size=0,
        edge_color="white",
        bgcolor="black",
        show=False,
        close=False
    )

    node_x = [G_static.nodes[n]["x"] for n in topk_nodes if n in G_static.nodes]
    node_y = [G_static.nodes[n]["y"] for n in topk_nodes if n in G_static.nodes]

    if len(node_x) == 0:
        print("⚠️  Aucun nœud top-k trouvé dans le graphe statique ! (vérifie les IDs)")
    else:
        ax.scatter(node_x, node_y, c="red", s=50, label="Top closeness", zorder=3)
        for i, (x, y) in enumerate(zip(node_x, node_y)):
            ax.text(x, y, f"{i+1}", color="white", fontsize=6, zorder=4)

    mode = "orienté" if oriented else "non orienté"
    ax.legend(facecolor="black", edgecolor="white", labelcolor="white")
    ax.set_title(f"{city} ({mode})", color="white")

    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, f"{city.replace(',', '').replace(' ', '_')}_{'oriented' if oriented else 'no_oriented'}.png")
    plt.savefig(path, dpi=300, bbox_inches="tight", facecolor="black")
    plt.close(fig)

    print(f"🖼️  Graphe sauvegardé dans : {path}")


# ------------------------------------------------------------
# Benchmark pour un type de graphe (orienté ou non orienté)
# ------------------------------------------------------------
def benchmark_city_graph(G_static, city, k=5, T_max=100, interval=(0, 100), oriented=True):
    """
    Exécute l’algorithme 2 pour un graphe donné (orienté ou non orienté)
    """
    mode = "orienté" if oriented else "non orienté"
    folder = f"visualisation/temporel_{'oriented' if oriented else 'no_oriented'}"
    print(f"   ▶️  Traitement du graphe {mode}...")

    try:
        # Extraction composante principale
        G_static = get_largest_component(G_static)
        num_nodes = len(G_static.nodes())
        num_edges = len(G_static.edges())

        print(f"   📊 Graphe {mode} : {num_nodes} nœuds, {num_edges} arêtes")

        # Conversion en graphe temporel
        G_temp = osmnx_to_temporal_graph(G_static, T_max=T_max, lambda_max=5, seed=42)

        # Exécution Algo 2
        start = time.perf_counter()
        result_topk = topk_temporal_closeness(G_temp, k=k, interval=interval)
        t_algo2 = time.perf_counter() - start

        print(f"⏱️  Temps Algo 2 ({mode}) = {t_algo2:.3f} s")

        # Extraction top-k
        topk_nodes = [node for _, node in result_topk]
        print(f"   🔺 Nœuds top-{k} ({mode}) : {topk_nodes}")

        # Visualisation
        plot_topk_on_city(G_static, topk_nodes, city, save_dir=folder, oriented=oriented)

        return {
            "city": city,
            "nodes": num_nodes,
            "edges": num_edges,
            "k": k,
            "algo2_time_s": round(t_algo2, 6),
            "oriented": oriented
        }

    except Exception as e:
        print(f"⚠️  Erreur pour {city} ({mode}) : {e}")
        import traceback
        traceback.print_exc()
        return None


# ------------------------------------------------------------
# Benchmark principal (pour chaque ville)
# ------------------------------------------------------------
def benchmark_city(city, k=5, T_max=100, interval=(0, 100)):
    """
    Lance le benchmark pour le graphe orienté et non orienté d'une même ville.
    """
    print(f"\n🏙️  {city}")

    results_city = []

    # --- Graphe orienté ---
    G_oriented = ox.graph_from_place(city, network_type="drive")
    res_oriented = benchmark_city_graph(G_oriented, city, k, T_max, interval, oriented=True)
    if res_oriented:
        results_city.append(res_oriented)

    # --- Graphe non orienté ---
    G_unoriented = G_oriented.to_undirected()
    res_unoriented = benchmark_city_graph(G_unoriented, city, k, T_max, interval, oriented=False)
    if res_unoriented:
        results_city.append(res_unoriented)

    return results_city


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

    print("=== 🧭 Benchmark Algo 2 — Top-k Temporal Closeness (orienté & non orienté) ===")

    for city in cities:
        city_results = benchmark_city(city, k=5)
        if city_results:
            results.extend(city_results)
        print(f"{'=' * 70}")

    # Sauvegarde CSV
    if results:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["city", "nodes", "edges", "k", "algo2_time_s", "oriented"]
            )
            writer.writeheader()
            writer.writerows(results)

        print(f"\n✅ Résultats enregistrés dans : {csv_path}")
        print(f"📊 {len(results)} exécutions terminées avec succès (2 par ville)")
    else:
        print("❌ Aucun résultat à enregistrer")

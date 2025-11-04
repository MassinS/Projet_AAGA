import time
import networkx as nx
import matplotlib.pyplot as plt
from classic_closeness.classic_closeness import closeness_centrality_all_nodes
from efficient_closeness import top_k_closeness
import os

def compare_top5():
    # --- Chargement du graphe Wiki-Vote ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(BASE_DIR, "..", "data", "Wiki-Vote.txt")
    print(f"📂 Chargement du graphe : {path}")
    G = nx.read_edgelist(path, create_using=nx.DiGraph(), nodetype=int)
    print(f"✅ Graphe chargé : {len(G.nodes())} sommets, {len(G.edges())} arêtes")

    # --- Classic closeness ---
    start_classic = time.perf_counter()
    classic = closeness_centrality_all_nodes(G)
    end_classic = time.perf_counter()
    classic_time = end_classic - start_classic
    top5_classic = sorted(classic, key=classic.get, reverse=True)[:5]

    # --- Optimized (Top-k) closeness ---
    start_opt = time.perf_counter()
    optimized = top_k_closeness.top_k_closeness(G, 5)
    end_opt = time.perf_counter()
    opt_time = end_opt - start_opt

    # --- Compute overlap ---
    intersection = set(top5_classic) & set(optimized)
    overlap = len(intersection) / 5 * 100

    print(f"\n📈 Pour Wiki-Vote :")
    print(f" - Top-5 Classic : {top5_classic}")
    print(f" - Top-5 Optimized : {optimized}")
    print(f" - Overlap : {overlap:.2f}%")
    print(f" - Temps Classic : {classic_time:.2f}s")
    print(f" - Temps Optimized : {opt_time:.2f}s")

    return overlap, classic_time, opt_time


# --- Exécution principale ---
overlap, classic_time, opt_time = compare_top5()

# --- Génération du graphique ---
plt.figure(figsize=(6,5))
plt.bar(["Classic", "Optimized"], [classic_time, opt_time], color=['skyblue', 'orange'])
plt.ylabel("Temps d'exécution (secondes)")
plt.title("Comparaison des temps — Wiki-Vote\nClassic vs Optimized Top-k Closeness")
plt.tight_layout()

# --- Sauvegarde automatique ---
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # niveau Projet_AAGA/src → Projet_AAGA
result_dir = os.path.join(base_dir, "resultat_comparaison")
os.makedirs(result_dir, exist_ok=True)

output_path = os.path.join(result_dir, "execution_times_WikiVote.png")
plt.savefig(output_path)
print(f"\n📊 Graphique enregistré dans : {output_path}")

# --- Résumé global ---
print(f"\n📄 Résumé : Overlap = {overlap:.2f}% | Classic = {classic_time:.2f}s | Optimized = {opt_time:.2f}s")

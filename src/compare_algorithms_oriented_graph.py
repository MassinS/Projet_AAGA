import time
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from utils.graph_utils import get_city_graph
from classic_closeness.classic_closeness import closeness_centrality_all_nodes
from efficient_closeness import top_k_closeness
import os

def compare_top5(city):
    """Compare les top-5 entre version classique et optimisée pour une ville donnée."""
    G = get_city_graph(city)
    n, m = len(G.nodes()), len(G.edges())

    print(f"📂 Chargement du graphe orienté local : {city}")
    print(f"✅ Graphe orienté prêt : {n} sommets, {m} arêtes")
    print("🔹 Type : dirigé")

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

    # --- Gain (%) et Speed-up ---
    gain = ((classic_time - opt_time) / classic_time * 100) if classic_time > 0 else 0
    speedup = (classic_time / opt_time) if opt_time > 0 else 0

    return city, n, m, classic_time, opt_time, gain, overlap, speedup


# --- Test sur plusieurs villes ---
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

for city in cities:
    city, n, m, t_classic, t_opt, gain, overlap, speedup = compare_top5(city)
    results.append({
        "Ville": city.split(",")[0],
        "|V|": n,
        "|E|": m,
        "Temps_classique (s)": round(t_classic, 3),
        "Temps_efficient (s)": round(t_opt, 3),
        "Gain (%)": round(gain, 2),
        "Speed-up (×)": round(speedup, 2),
        "Overlap (%)": round(overlap, 2)
    })
    print(f"{city}: overlap={overlap:.1f}%  gain={gain:.1f}%  speedup={speedup:.2f}×")

# --- Conversion en DataFrame ---
df = pd.DataFrame(results)

# --- Création du dossier de sortie ---
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
result_dir = os.path.join(base_dir, "resultat_comparaison")
os.makedirs(result_dir, exist_ok=True)

# --- Sauvegarde du tableau résumé ---
csv_path = os.path.join(result_dir, "resume_oriented.csv")
df.to_csv(csv_path, index=False)
print(f"\n📄 Tableau résumé sauvegardé dans : {csv_path}\n")

# --- Affichage Markdown dans la console ---
print(df.to_markdown(index=False))

# ==========================================================
# 1️⃣ Graphique en barres (comparaison classique / efficient)
# ==========================================================
plt.figure(figsize=(10,6))
x = range(len(df))
plt.bar(x, df["Temps_classique (s)"], width=0.4, label='Classic', alpha=0.7)
plt.bar([i + 0.4 for i in x], df["Temps_efficient (s)"], width=0.4, label='Efficient', alpha=0.7)

plt.xticks([i + 0.2 for i in x], df["Ville"], rotation=45, ha='right')
plt.ylabel("Temps d'exécution (secondes)")
plt.title("Comparaison des temps d'exécution\nGraphe orienté : Classic vs Efficient")
plt.legend()
plt.tight_layout()

bar_path = os.path.join(result_dir, "bar_oriented_comparison.png")
plt.savefig(bar_path)
print(f"📊 Graphique en barres enregistré dans : {bar_path}")

# ==========================================================
# 2️⃣ Nuage de points (log-scale)
# ==========================================================
plt.figure(figsize=(8,6))
plt.scatter(df["|V|"], df["Temps_classique (s)"], color='blue', label='Classic', s=80)
plt.scatter(df["|V|"], df["Temps_efficient (s)"], color='orange', label='Efficient', s=80, marker='x')

plt.yscale("log")
plt.xlabel("Nombre de sommets |V|")
plt.ylabel("Temps d'exécution (s) [échelle logarithmique]")
plt.title("Comparaison des temps d'exécution (log-scale)\nGraphe orienté : Classic vs Efficient")
plt.legend()
plt.grid(True, which="both", linestyle="--", alpha=0.6)
plt.tight_layout()

scatter_path = os.path.join(result_dir, "scatter_oriented_logscale.png")
plt.savefig(scatter_path)
print(f"📊 Graphique (nuage de points) enregistré dans : {scatter_path}")

# ==========================================================
# 3️⃣ Graphique du speed-up
# ==========================================================
plt.figure(figsize=(8,5))
plt.bar(df["Ville"], df["Speed-up (×)"], color="green", alpha=0.7)
plt.xticks(rotation=45, ha='right')
plt.ylabel("Speed-up (×)")
plt.title("Facteur d'accélération (Classic / Efficient)\nGraphe orienté")
plt.tight_layout()

speedup_path = os.path.join(result_dir, "speedup_oriented.png")
plt.savefig(speedup_path)
print(f"⚡ Graphique de speed-up enregistré dans : {speedup_path}")

# --- Moyenne du recouvrement ---
avg_overlap = df["Overlap (%)"].mean()
print(f"\nMoyenne du recouvrement : {avg_overlap:.2f}%")

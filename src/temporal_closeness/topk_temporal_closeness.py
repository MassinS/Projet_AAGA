# ==========================================
# Algorithm 2 : Top-k Temporal Closeness
# ==========================================

from temporal_graph import TemporalGraph
from fastest_path import fastest_paths
import heapq
import time

# --------------------------------------------------
# Fonction de calcul de la borne supérieure
# --------------------------------------------------
def compute_upper_bound(S_F, len_T, len_R, len_F, d_next, delta, lambda_min):
    """Calcule la borne supérieure de la closeness courante."""
    return S_F + (len_T / d_next) + ((len_R - len_F - len_T) / (d_next + delta + lambda_min))


# --------------------------------------------------
# Fonction principale
# --------------------------------------------------
def topk_temporal_closeness(G: TemporalGraph, k: int, interval=(0, 100)):
    """
    Implémente l'algorithme 2 du papier :
    Calcule le Top-k des sommets selon la centralité de proximité temporelle.
    """
    # --- Initialisation du top-k global ---
    topk = []      # [(closeness, node)]
    B_k = 0.0      # seuil actuel minimal dans le top-k

    # --- Trier les sommets par degré sortant (priorité aux "sources fortes") ---
    sources = sorted(G.V, key=lambda u: len(G.adj[u]), reverse=True)

    delta = 0.0
    lambda_min = min(e.l for edges in G.adj.values() for e in edges)

    # --- Boucle principale sur chaque sommet source ---
    for u in sources:

        # 1️⃣ Exécuter l’algo 1 pour récupérer les distances minimales
        d = fastest_paths(G, source=u, interval=interval)

        # 2️⃣ Construire R = sommets atteignables
        R = [v for v in d if d[v] < float("inf")]
        len_R = len(R)
        if len_R <= 1:
            continue  # rien d'atteignable

        # 3️⃣ Variables de suivi
        F = set()
        T = set()
        S_F = 0.0
        d_next = 1.0

        # 4️⃣ Parcours des sommets atteignables triés par durée
        sorted_nodes = sorted([v for v in R if v != u], key=lambda x: d[x])

        for i, v in enumerate(sorted_nodes):
            duration = d[v]
            if duration <= 0:
                continue

            F.add(v)
            S_F += 1.0 / duration

            # mise à jour de la "frontière"
            for e in G.adj[v]:
                if e.v not in F:
                    T.add(e.v)

            # prochaine durée
            if i + 1 < len(sorted_nodes):
                d_next = d[sorted_nodes[i + 1]]
            else:
                d_next = duration  # dernière itération

            # calcul de la borne supérieure
            c_hat = compute_upper_bound(S_F, len(T), len_R, len(F), d_next, delta, lambda_min)

            # test de pruning
            if c_hat < B_k:
                break

        # 5️⃣ Calcul final de la closeness du sommet u
        c_u = S_F

        # 6️⃣ Mise à jour du Top-k global
        heapq.heappush(topk, (c_u, u))
        if len(topk) > k:
            heapq.heappop(topk)
        B_k = topk[0][0]

    # --- Résultat final ---
    topk_sorted = sorted(topk, reverse=True)

    # ✅ Retourne la liste [(closeness, node)] pour la visualisation et le benchmark
    return topk_sorted


# --------------------------------------------------
# Test local simple
# --------------------------------------------------
if __name__ == "__main__":
    G = TemporalGraph()
    G.add_edge("A", "B", 1, 2)
    G.add_edge("A", "C", 2, 3)
    G.add_edge("B", "D", 4, 2)
    G.add_edge("C", "D", 6, 1)
    G.add_edge("D", "E", 8, 1)
    G.add_edge("B", "E", 10, 2)
    G.add_edge("E", "F", 12, 1)

    print("=== Graphe ===")
    print(G)
    print()

    k = 3
    interval = (0, 20)

    start_time = time.perf_counter()
    res = topk_temporal_closeness(G, k=k, interval=interval)
    end_time = time.perf_counter()

    print("\n⏱️ Temps total d'exécution : {:.6f} secondes".format(end_time - start_time))
    print("Résultat top-k :", res)

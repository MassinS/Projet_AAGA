# ==========================================
# Algorithm 2 : Top-k Temporal Closeness
# ==========================================

from temporal_graph import TemporalGraph
from fastest_path import incremental_fastest_paths
import heapq
import time

# L'algorithme de calcul de la borne supérieure de la closeness
def compute_upper_bound(S_F, len_T, len_R, len_F, d_next, delta, lambda_min):
    """Calcule la borne supérieure de la closeness courante."""
    return S_F + (len_T / d_next) + ((len_R - len_F - len_T) / (d_next + delta + lambda_min))

# Algorithme principal de calcul du top-k temporal closeness avec pruning
# L'idée principale est d'utiliser le générateur incremental_fastest_paths pour explorer le graphe temporel
# et de calculer une borne supérieure de la closeness à chaque étape pour décider si on continue l'exploration ou pas.
def topk_temporal_closeness(G: TemporalGraph, k: int, interval=(0, 100)):
    """
    Calcule le Top-k des sommets selon la centralité temporelle,
    avec pruning (arrêt anticipé) pendant le parcours.
    """
    topk = []      # [(closeness, node)]
    B_k = 0.0      # seuil minimal du top-k

    sources = sorted(G.V, key=lambda u: len(G.adj[u]), reverse=True)

    delta = 0.0
    lambda_min = min(e.l for edges in G.adj.values() for e in edges)

    for u in sources:
        S_F = 0.0
        F = set()
        T = set()
        len_R = len(G.V)  # approximation du nombre de sommets atteignables

        # On explore le graphe temporel en direct
        for (v, duration, d_next) in incremental_fastest_paths(G, u, interval):
            if duration == 0:
                continue

            F.add(v)
            S_F += 1.0 / duration

            # mise à jour de la frontière
            for e in G.adj[v]:
                if e.v not in F:
                    T.add(e.v)

            # calcul de la borne supérieure
            c_hat = compute_upper_bound(S_F, len(T), len_R, len(F), d_next, delta, lambda_min)

            # pruning (si la borne < seuil top-k)
            if c_hat < B_k:
                break

        # closeness finale pour ce sommet
        c_u = S_F

        # mise à jour du top-k
        heapq.heappush(topk, (c_u, u))
        if len(topk) > k:
            heapq.heappop(topk)
        B_k = topk[0][0]

    return sorted(topk, reverse=True)


# Test local 
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

    print("\n Temps total d'exécution : {:.6f} secondes".format(end_time - start_time))
    print("Résultat top-k :", res)

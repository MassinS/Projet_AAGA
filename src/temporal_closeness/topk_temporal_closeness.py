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
    # Préparation du Top-k global (min-heap)
    topk = []      # [(closeness, node)]
    B_k = 0.0      # seuil actuel (valeur minimale du Top-k)

    # traiter d’abord les sommets à fort degré sortant.
    sources = sorted(G.V, key=lambda u: len(G.adj[u]), reverse=True)

    delta = 0.0
    lambda_min = min(e.l for edges in G.adj.values() for e in edges)

    for u in sources:
        print(f"\n🔹 Calcul pour la source {u}")

        # 1️⃣ Exécuter l’algo 1 pour récupérer les distances minimales
        d = fastest_paths(G, source=u, interval=interval)

        # 2️⃣ Construire R = sommets atteignables
        R = [v for v in d if d[v] < float("inf")]
        len_R = len(R)

        # 3️⃣ Variables de suivi
        F = set()
        T = set()
        S_F = 0.0
        d_next = 1.0  # estimation initiale

        # 4️⃣ Simulation de la progression (on parcourt les sommets atteignables triés par durée)
        sorted_nodes = sorted([v for v in R if v != u], key=lambda x: d[x])

        for i, v in enumerate(sorted_nodes):
            duration = d[v]
            F.add(v)
            S_F += 1.0 / duration

            # mise à jour de la "frontière" : voisins pas encore fixés
            for e in G.adj[v]:
                if e.v not in F:
                    T.add(e.v)

            # prochaine durée
            if i + 1 < len(sorted_nodes):
                d_next = d[sorted_nodes[i + 1]]
            else:
                d_next = duration  # dernière itération

            # calcul de la borne
            c_hat = compute_upper_bound(S_F, len(T), len_R, len(F), d_next, delta, lambda_min)
            print(f"  Étape {i+1} → F={len(F)} T={len(T)} reste={len_R - len(F) - len(T)} | S_F={S_F:.3f} | d_next={d_next:.2f} | borne={c_hat:.3f}")

            # test de pruning
            if c_hat < B_k:
                print(f"   ⏹  Arrêt anticipé : {c_hat:.3f} < B_k={B_k:.3f}")
                break

        c_u = S_F
        print(f"✅ Closeness({u}) = {c_u:.3f}")

        # Mise à jour du Top-k
        heapq.heappush(topk, (c_u, u))
        if len(topk) > k:
            heapq.heappop(topk)  # garde seulement les k meilleurs
        B_k = topk[0][0]  # seuil minimal actuel

        print(f"📊 Top-{k} actuel : {sorted(topk, reverse=True)} (B_k={B_k:.3f})")

    print("\n🏁 Résultat final :")
    for val, node in sorted(topk, reverse=True):
        print(f"  {node} → {val:.3f}")


if __name__ == "__main__":
    # 1️⃣ Création d’un graphe temporel
    G = TemporalGraph()
    G.add_edge("A", "B", 1, 2)   # active de 1 à 3
    G.add_edge("A", "C", 2, 3)   # active de 2 à 5
    G.add_edge("B", "D", 4, 2)   # active de 4 à 6
    G.add_edge("C", "D", 6, 1)   # active de 6 à 7
    G.add_edge("D", "E", 8, 1)   # active de 8 à 9
    G.add_edge("B", "E", 10, 2)  # active de 10 à 12
    G.add_edge("E", "F", 12, 1)  # active de 12 à 13

    print("=== Graphe ===")
    print(G)
    print()

    # 2️⃣ Lancer l’algorithme Top-k depuis la source A
    k = 3
    interval = (0, 20)
    print(f"=== Top-{k} Temporal Closeness dans l'intervalle {interval} ===")
    
    start_time = time.perf_counter()
    res = topk_temporal_closeness(G, k=k, interval=interval)
    end_time = time.perf_counter()
    print(f"\n⏱️ Temps total d'exécution : {end_time - start_time:.6f} secondes")
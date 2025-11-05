import networkx as nx
from collections import deque
import time
def closeness_centrality_all_nodes(G):
    """
    Compute closeness centrality for all nodes in an unweighted, undirected graph.
    Based on Algorithm 1 from the course.
    """
    closeness = {}
    n = len(G)  # nombre total de sommets du graphe

    for v in G.nodes():
        
        # 1 Initialisation des distances
        dist = {u: float('inf') for u in G.nodes()}
        dist[v] = 0

        # 2 Parcours en largeur (BFS)
        Q = deque([v])
        while Q:
            x = Q.popleft()
            for y in G.neighbors(x):
                if dist[y] == float('inf'):
                    dist[y] = dist[x] + 1
                    Q.append(y)

        # 3 Sommation des distances (uniquement les sommets atteignables)
        reachable = [u for u in G.nodes() if dist[u] < float('inf')]
        S = sum(dist[u] for u in reachable if u != v)
        r_v = len(reachable)        # |R_v|

        # 4 Calcul de la centralité normalisée
        if S > 0 and r_v > 1:
            # closeness[v] = 1 / S # Méthode de cours "non normaliser"
            closeness[v] = ((r_v - 1) ** 2) / ((n - 1) * S)
        else:
            closeness[v] = 0.0  # sommet isolé ou sans voisins atteignables
        #print(f"nombre de sommets atteignables depuis {v}: {r_v} et somme des distances: {S}")
    return closeness

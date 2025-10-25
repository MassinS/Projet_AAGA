import networkx as nx
from collections import defaultdict
from sketch import Sketch   # ✅ nom correct

def prep(G, k):
    # μ = plus petit poids d'arête (1 si non pondéré)
    if nx.get_edge_attributes(G, 'weight'):
        mu = min(data['weight'] for _, _, data in G.edges(data=True))
    else:
        mu = 1.0

    #  Initialisation 
    n = 0
    V_hat = {}        # Sketch global de chaque sommet
    S_hat = {}        # Somme estimée des distances
    V = defaultdict(dict)  # Sketch par couche : V[v][τ]

    #  Phase 1 : initialisation de chaque sommet 
    for v in G.nodes():
        V_hat[v] = Sketch()
        V_hat[v].add(v)   
        S_hat[v] = 0

    #  Phase 2 : propagation sur les arêtes 
        preds = G.predecessors(v) if G.is_directed() else G.neighbors(v)
        for p in preds:
         w = G[p][v].get('weight', 1.0)
         tau = round(w / mu) 
         if tau not in V[p]:
            V[p][tau] = Sketch()
         V[p][tau].merge(V_hat[v])  # union (max registre par registre)
         n=max(n,tau)
    # Phase 3 :construction par couche
    for i in range(0, n, mu):
       for v in G.nodes():
          Vprime=V_hat[v].merge(V[v][i])
          if V_hat[v]!=Vprime:
             S_hat[v]=S_hat[v]+i*(Vprime.count - V_hat.count)
             V_hat[v]=Vprime
             preds = G.predecessors(v) if G.is_directed() else G.neighbors(v)
             for p in preds:
                w = G[p][v].get('weight', 1.0)
                tau = round(((i+w)/w) / mu)
                if tau not in V[p]:
                   V[p][tau] = Sketch()
                V[p][tau].merge(V_hat[v])
                n=max(n,tau)

    return V_hat, S_hat

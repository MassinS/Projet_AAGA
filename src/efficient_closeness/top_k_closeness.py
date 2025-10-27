import math
import heapq
import networkx as nx
from collections import defaultdict
from Skecth import Sketch   

def prep(G):
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

def schedule(G, V_hat, S_hat):
    """
    Construit la table de planification (schedule) :
      - détermine les sommets sources (PFS)
      - détermine les sommets dépendants (Δ-PFS)
    selon les coûts estimés basés sur les sketches.
    """
    sources = []       # sommets a exécutés avec PFS
    optimized = []     # couples (v, p) a exécutés avec optimized-PFS(v,p)
    gamma=1.79
    V_hat, S_hat = prep(G)
    
    def poids(u, v):
        return G[u][v].get('weight', 1.0)

    # Fonction count() du sketch
    def count(v):
        return V_hat[v].count() if hasattr(V_hat[v], "count") else len(V_hat[v])
    
    # Fonction d'estimation de la somme des distances promues
    def sigma_hat(v, p):
        c_v = count(v)
        c_p = count(p)
        if c_v == 0: 
            return 0
        return (
            poids(v, p) * c_p +
            S_hat[p] -
            (c_p / c_v) * S_hat[v]
        )

    # Fonction d'estimation du nombre de sommets promus
    def promoted_vertices(v, p):
        sigma = sigma_hat(v, p)
        if sigma <= 0: 
            return 0
        c_p = count(p)
        w = poids(v, p)
        s_p = S_hat[p]
        return 0.82 * (sigma ** 0.96) * (c_p ** 0.23) * ((w) ** -0.83) * (s_p ** 0.16)

    # Boucle principale : pour chaque sommet, choisir PFS ou optimized-PFS
    for v in G.nodes():
        t_v = count(v) * math.log(count(v) + 1)  # coût estimé du PFS
        best_parent = None
        best_cost = float('inf')

        # Évaluer le coût optimized-PFS pour chaque voisin prédécesseur
        preds = G.predecessors(v) if G.is_directed() else G.neighbors(v)
        for p in preds:
            new_nodes = max(count(v) - count(p), 0)
            promoted = promoted_vertices(v, p)
            V_vp = new_nodes + promoted
            if V_vp <= 0:
                continue
            t_vp = gamma * V_vp * math.log(V_vp + 1)
            if t_vp < best_cost:
                best_cost = t_vp
                best_parent = p

        # Choisir entre PFS ou optimized-PFS
        if t_v <= best_cost or best_parent is None:
            sources.append(v)
        else:
            optimized.append((v, best_parent))
        S = {}
        for (v, p) in optimized:
         if p not in S:
            S[p] = []
         S[p].append(v)

    return S
def Start(S):
    all_nodes = set(S.keys()) | {child for children in S.values() for child in children}
    non_sources = {child for children in S.values() for child in children}
    sources = list(all_nodes - non_sources)
    return sources


def prune(v,L,s,teta_A,S,delta_v,G):
    Inf={}
    Sup={}
    phi={}
    m = len(G.nodes())
    if G.is_directed():
        path_to_v   = nx.ancestors(G, v)
        path_from_v = nx.descendants(G, v)
    else:
        path_to_v = path_from_v = nx.node_connected_component(G, v)
    for u in path_to_v:
        Inf[u]=len(L)
    for u in path_from_v:
        Sup[u]=len(L)
    Q = []
    heapq.heappush(Q, (0.0, v))
    while Q:
        (dist_u, u) = heapq.heappop(Q)
        sprime=s-((len(L)-Inf[u]*delta_v)-(dist_u*Sup[u]))
        cprime=((Sup[u]-1))**2/(m-1)*sprime
        if cprime-teta_A<phi[u]:
            phi[u]=cprime-teta_A
            if u in S:  
             for uprime in S[u]:  
              w_u = G[u][uprime].get('weight', 1.0)
              heapq.heappush(Q, (dist_u +  w_u, uprime))

            has_successors = (u in S and len(S[u]) > 0)
            if (cprime < teta_A) and (not has_successors):
                # Retirer u des enfants de tous les parents
                for parent, children in list(S.items()):
                    if u in children:
                        children.remove(u)

                # Supprimer la clé u si elle existe
                if u in S:
                    del S[u]
            
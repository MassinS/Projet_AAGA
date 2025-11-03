import math
import time
from collections import deque
import heapq
import networkx as nx
from collections import defaultdict
from efficient_closeness import Sketch   

def prep(G):
    """
    PREP (Section V-B du papier SUNYA), version corrigée.
    Marche pour graphe dirigé (MultiDiGraph) ou non dirigé.
    Produit:
      - V_hat[v] ~ estimation du nb de sommets atteignables depuis v
      - S_hat[v] ~ estimation de la somme des distances depuis v
    """

    # 1. Trouver μ = plus petit poids d'arête (évite 0)
    mu = min(
        (data.get("weight", 1.0) for _, _, data in G.edges(data=True)),
        default=1.0
    )
    if mu <= 0:
        mu = 1.0  # sécurité

    # 2. Structures
    V_hat = {}   # sketch global accumulé par sommet
    S_hat = {}   # somme estimée des distances
    # V[x][τ] = sketch à "livrer" à x à distance arrondie τ
    V = defaultdict(lambda: defaultdict(Sketch.Sketch))

    n = 1  # profondeur max connue pour le moment

    # 3. Init: chaque sommet "se connaît lui-même"
    for v in G.nodes():
        V_hat[v] = Sketch.Sketch()
        V_hat[v].add(v)
        S_hat[v] = 0.0

    # 4. Propagation couche 1 (voisins directs)
    for v in G.nodes():
        succs = G.successors(v) if G.is_directed() else G.neighbors(v)
        for succ in succs:
            w = G[v][succ].get("weight", 1.0)
            hop = int(math.ceil(w / mu))
            if hop < 1:
                hop = 1
            V[succ][hop].merge(V_hat[v])   # succ reçoit ce que v connaît
            n = max(n, hop)

    # 5. Expansion par couches croissantes
    i = 1
    while i <= n:
        for v in G.nodes():
            if i not in V[v]:
                continue

            # fusionner ce qui "arrive" à v à la couche i
            Vprime = V_hat[v].clone()
            Vprime.merge(V[v][i])

            delta = Vprime.count() - V_hat[v].count()
            if delta > 0:
                # on met à jour S_hat[v] avec i * (#nouveaux sommets)
                S_hat[v] += i * delta

                # on adopte le sketch élargi
                V_hat[v] = Vprime

                # propager cette nouvelle connaissance vers les successeurs
                succs = G.successors(v) if G.is_directed() else G.neighbors(v)
                for succ in succs:
                    w = G[v][succ].get("weight", 1.0)
                    hop = int(math.ceil(w / mu))
                    if hop < 1:
                        hop = 1
                    new_tau = i + hop

                    # on ajoute AU SUCCESSEUR, et on lui envoie V_hat[v]
                    V[succ][new_tau].merge(V_hat[v])

                    # mettre à jour la profondeur max
                    if new_tau > n:
                        n = new_tau
        i += 1


    return V_hat, S_hat




def schedule(G, V_hat, S_hat):
    """
    Construit la table de planification (schedule) :
      - détermine les sommets sources (PFS)
      - détermine les sommets dépendants (Δ-PFS)
    selon les coûts estimés basés sur les sketches.
    """
    gamma = 1.79
    S = {}                 
    sources = []           # sommets à exécuter avec PFS
    optimized = []         # couples (v, p) à exécuter avec Δ-PFS

    def poids(u, v):
     if G.has_edge(u, v):
        return G[u][v].get('weight', 1.0)
     elif G.has_edge(v, u):
        return G[v][u].get('weight', 1.0)
     else:
        return 1.0

    def count(v):
        return V_hat[v].count() if hasattr(V_hat[v], "count") else len(V_hat[v])

    def sigma_hat(v, p):
        c_v = count(v)
        c_p = count(p)
        if c_v == 0:
            return 0
        return poids(v, p) * c_p + S_hat[p] - (c_p / c_v) * S_hat[v]

    def promoted_vertices(v, p):
        sigma = max(sigma_hat(v, p), 1.0)
        if sigma <= 0:
            return 0
        c_p = max(count(p), 1.0)
        w = max(poids(v, p), 1.0)
        s_p = S_hat[p] if S_hat[p] > 1.0 else 1.0
        return 0.82 * (sigma ** 0.96) * (c_p ** 0.23) / ((w ** 0.83) * (s_p ** 0.16))

    # --- Boucle principale ---
    for v in G.nodes():
        t_v = count(v) * math.log(count(v) + 1)
        best_parent = None
        best_cost = float("inf")

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

        if t_v < best_cost or best_parent is None:
            sources.append(v)
        else:
            optimized.append((v, best_parent))

    # --- Construction du dictionnaire S après la boucle ---
    for (v, p) in optimized:
        if p not in S:
            S[p] = []
        S[p].append(v)

    
    for src in sources:
        if src not in S:
            S[src] = []

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
    Sup[v]=Inf[v]=len(L)
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
        Inf_u = Inf.get(u, len(L))
        Sup_u = Sup.get(u, len(L))
        sprime=s-(((len(L)-Inf_u)*delta_v)-(dist_u*Sup_u))
        cprime=((Sup_u-1)**2)/((m-1)*sprime)
        if cprime-teta_A<phi.get(u, float('inf')):
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



def PFS(G, v):
    dist = {v: 0}
    s = 0
    delta_v = 0
    visited = {v}
    Q = deque([v])
    adj = G._adj

    while Q:
        n = Q.popleft()
        l = dist[n]
        s += l
        delta_v = l
        for vprime in adj[n]:
            if vprime not in visited:
                visited.add(vprime)
                dist[vprime] = l + 1
                Q.append(vprime)
    return dist, s, delta_v

def optimized_PFS(G, v, p, L, s, delta_p):
    """
    Δ-PFS : version optimisée du PFS classique.
    Réutilise les distances déjà calculées pour p afin de calculer celles de v.
    """
    # Distance du parent p et distance vers v
    alpha_p = L[p]
    w_pv = G[p][v].get('weight', 1.0)

    # ✅ on ajoute la distance, pas on la soustrait
    alpha_v = alpha_p + w_pv

    # Copie locale des distances
    L_v = dict(L)
    s_v = s + len(L_v) * w_pv
    delta_v = delta_p + w_pv

    # journal des modifications (pour rollback)
    log_level = {}

    # file de priorité
    Q = [(alpha_v, v)]
    L_v[v] = alpha_v
    log_level[v] = None

    while Q:
        l, n = heapq.heappop(Q)

        for vprime, data in G[n].items():
            w = data.get('weight', 1.0)
            lprime = l + w
            old = L_v.get(vprime)

            if old is None or lprime < old:
                # on note l'ancienne valeur pour rollback
                log_level[vprime] = old
                L_v[vprime] = lprime
                heapq.heappush(Q, (lprime, vprime))

                # mise à jour du score cumulé et de la distance max
                s_v += (lprime - alpha_v)
                delta_v = max(delta_v, lprime - alpha_v)

    return L_v, s_v, delta_v, log_level


def rollback(L, log_level):
    """
    Annule les modifications de distances dans L selon le journal.
    (important pour la récursivité du Δ-PFS)
    """
    for n, old in log_level.items():
        if old is None:
            L.pop(n, None)
        else:
            L[n] = old

def top_k_closeness(G, k):
    A = {}
    V = len(G.nodes())
    V_hat, S_hat = prep(G)
    S = schedule(G, V_hat, S_hat)
    dead = set()
    for v in Start(S):
        #start_optimized = time.perf_counter()
        (L, s, delta_p) = PFS(G, v)
        #end_optimized = time.perf_counter()
        #print(f"PFS Time: {end_optimized - start_optimized:.4f} seconds")
        process(G, v, L, s, A, S, k, V, delta_p, dead)  
    return A


def update_topk(A, p, c_p, k):
    """
    Maintient dynamiquement le top-k des plus fortes centralités.
    Retourne le nouveau seuil θ_A (min des top-k).
    """
    # Si le nœud est déjà dans A → simple mise à jour
    if p in A:
        if c_p > A[p]:
            A[p] = c_p
        # seuil inchangé
        return min(A.values()) if len(A) == k else 0

    # Si pas encore k nœuds, on ajoute directement
    if len(A) < k:
        A[p] = c_p
        return min(A.values()) if len(A) == k else 0

    # Sinon, on remplace le plus petit si c_p est meilleur
    min_node = min(A, key=A.get)
    if c_p > A[min_node]:
        del A[min_node]
        A[p] = c_p

    return min(A.values()) if len(A) == k else 0


def process(G, p, L, s, A, S, k, V, delta_p, dead):
    """
    Étape de traitement récursif du sommet p :
    - calcule la centralité de p
    - met à jour le top-k
    - propage à ses successeurs planifiés
    """
    if p in dead:
        return

    # --- 1. Calcul de la centralité
    if s <= 0:
        return  # sécurité
    c_p = ((len(L) - 1) ** 2) / ((V - 1) * s)

    # --- 2. Mise à jour du top-k et récupération du seuil θ_A
    theta_A = update_topk(A, p, c_p, k)
    prune(p, L, s, theta_A, S, delta_p, G)
   

    # --- 3. Propagation à chaque successeur planifié
    for v in S.get(p, []):
        L, s2, delta_v, log_level = optimized_PFS(G, v, p, L, s, delta_p)
        process(G, v, L, s2, A, S, k, V, delta_v, dead)
        rollback(L, log_level)  # ✅ rollback sur la même référence

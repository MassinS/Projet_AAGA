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
      # 0) Références locales (micro-opt Python)
    log1p = math.log1p
    is_dir = G.is_directed()

    # 1) PRE-CACHES — évite hasattr, .count() répétés et accès G coûteux
    #    count_map[v] = |V̂_v|   (Sketch.count() une seule fois)
    count_map = {v: (V_hat[v].count() if hasattr(V_hat[v], "count") else len(V_hat[v]))
                 for v in G.nodes()}
    #    preds_map[v] : liste de prédécesseurs (ou voisins si non orienté), calculée une fois
    if is_dir:
        preds_map = {v: list(G.predecessors(v)) for v in G.nodes()}
    else:
        preds_map = {v: list(G.neighbors(v)) for v in G.nodes()}

    #    poids_map[(u,v)] = weight (évite has_edge + double accès dict)
    #    NB: pour graphe non orienté on indexe les deux sens.
    poids_map = {}
    for u, v, data in G.edges(data=True):
        w = data.get('weight', 1.0)
        poids_map[(u, v)] = w
        if not is_dir:
            poids_map[(v, u)] = w

    # 2) Helpers pur dictionnaire (sans NetworkX)
    def poids(u, v):
        # accès O(1) sans has_edge
        return poids_map.get((u, v), 1.0)

    # 3) Pré-calcul léger sur S_hat pour accès direct
    #    (pas indispensable, mais évite dict lookup profond dans la boucle)
    S_hat_map = S_hat  # alias local

    # 4) Fonctions de coût (toutes en version "no-overhead")
    def sigma_hat(v, p):
        c_v = count_map[v]
        if c_v == 0:
            return 0.0
        c_p = count_map[p]
        return poids(p, v) * c_p + S_hat_map[p] - (c_p / c_v) * S_hat_map[v]

    def promoted_vertices(v, p):
        # bornes et stabilisation pour éviter divisions/multiplications inutiles
        c_p = count_map[p]
        if c_p <= 0:
            return 0.0
        s = sigma_hat(v, p)
        if s < 1.0:
            s = 1.0
        w = poids(p, v)
        if w < 1.0:
            w = 1.0
        s_p = S_hat_map[p]
        if s_p < 1.0:
            s_p = 1.0
        # 0.82 * s^0.96 * c_p^0.23 / ( w^0.83 * s_p^0.16 )
        return 0.82 * (s ** 0.96) * (c_p ** 0.23) / ( (w ** 0.83) * (s_p ** 0.16) )

    # 5) Boucle principale
    S = {}
    sources = []
    optimized = []

    for v in G.nodes():
        cv = count_map[v]
        t_v = cv * log1p(cv)                 # (A) utiliser log1p : plus rapide/robuste
        best_parent = None
        best_cost = float('inf')

        # Itérer sur les prédécesseurs (déjà listés)
        for p in preds_map[v]:
            # (B) new_nodes = max(cv - cp, 0) — tout en cache
            cp = count_map[p]
            new_nodes = cv - cp
            if new_nodes <= 0:
                # bornes : si pas de nouveaux sommets, on teste quand même le "promoted"
                new_nodes = 0

            # (C) **Lower bound rapide** : si même la borne inf ne bat pas best_cost courant,
            #     on évite de calculer 'promoted_vertices' (cher)
            if new_nodes > 0:
                t_lb = gamma * new_nodes * log1p(new_nodes)
                if t_lb >= best_cost:
                    continue  # impossible d'améliorer → skip ce parent

            # (D) Calcul du terme promu (cher) uniquement si utile
            promoted = promoted_vertices(v, p)  # utilise sigma_hat avec caches
            V_vp = new_nodes + promoted
            if V_vp <= 0:
                continue

            t_vp = gamma * V_vp * log1p(V_vp)
            if t_vp < best_cost:
                best_cost = t_vp
                best_parent = p

        # Choix final
        if (t_v < best_cost) or (best_parent is None):
            sources.append(v)
        else:
            optimized.append((v, best_parent))

    # 6) Construction S (sans branches inutiles)
    #    On évite les "if p not in S" en une passe
    for p, children in _group_by_parent(optimized).items():
        S[p] = children
    # garantir une entrée pour chaque source
    for src in sources:
        if src not in S:
            S[src] = []

    return S


def _group_by_parent(pairs):
    """
    Utility: regroupe [(v,p), ...] en {p: [v1, v2, ...]}
    """
    out = {}
    for v, p in pairs:
        lst = out.get(p)
        if lst is None:
            out[p] = [v]
        else:
            lst.append(v)
    return out

def Start(S):
    all_nodes = set(S.keys()) | {child for children in S.values() for child in children}
    non_sources = {child for children in S.values() for child in children}
    sources = list(all_nodes - non_sources)
    return sources


def prune(v,L,s,teta_A,S,delta_v,G,neighbors_cache,weights_cache):
    # --- 1️⃣ Préparation (caches et constantes)
    len_L = len(L)
    m = len(G.nodes())

    # caches locaux
    phi = {}
    Inf = {v: len_L}
    Sup = {v: len_L}

    # --- 2️⃣ Initialisation
    Q = [(0.0, v)]

    # --- 3️⃣ Parcours
    while Q:
        dist_u, u = heapq.heappop(Q)

        Inf_u = Inf.get(u, len_L)
        Sup_u = Sup.get(u, len_L)

        sprime = s - (((len_L - Inf_u) * delta_v) - (dist_u * Sup_u))
        cprime = ((Sup_u - 1) ** 2) / ((m - 1) * sprime)

        # --- test de pruning
        if cprime - teta_A < phi.get(u, float('inf')):
            phi[u] = cprime - teta_A

            # --- exploration des successeurs planifiés uniquement
            successors = S.get(u)
            if successors:
                for uprime in successors:
                    w_u = weights_cache.get((u, uprime), 1.0)
                    heapq.heappush(Q, (dist_u + w_u, uprime))

            # --- condition de suppression
            has_successors = bool(successors)
            if (cprime < teta_A) and not has_successors:
                # ✅ suppression plus rapide (pas de double boucle)
                for parent, children in S.items():
                    try:
                        children.remove(u)
                    except ValueError:
                        pass
                S.pop(u, None)



def PFS(G, v,neighbors_cache):
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
        for vprime in neighbors_cache[n]:
            if vprime not in visited:
                visited.add(vprime)
                dist[vprime] = l + 1
                Q.append(vprime)
    return dist, s, delta_v

def optimized_PFS(G, v, p, L, s, delta_p,neighbors_cache,weights_cache):
    """
    Δ-PFS : version optimisée du PFS classique.
    Réutilise les distances déjà calculées pour p afin de calculer celles de v.
    """
     # --- 2️⃣ Distances initiales
    alpha_p = L[p]
    w_pv = weights_cache.get((p, v), 1.0)
    alpha_v = alpha_p + w_pv

    # ⚡ Pas de copie complète : on va modifier L directement
    # mais on garde trace des modifs pour rollback
    log_level = {}
    s_v = s + len(L) * w_pv
    delta_v = delta_p + w_pv

    # --- 3️⃣ Initialisation de la file
    Q = [(alpha_v, v)]
    old_val = L.get(v)
    log_level[v] = old_val  # journaliser même si None
    L[v] = alpha_v

    # --- 4️⃣ Parcours Dijkstra-like (réutilise L directement)
    heapq_heapify = heapq.heapify
    heapq_heappop = heapq.heappop
    heapq_heappush = heapq.heappush

    while Q:
        l, n = heapq_heappop(Q)

        for vprime in neighbors_cache[n]:
            w = weights_cache.get((n, vprime), 1.0)
            lprime = l + w
            old = L.get(vprime)

            if old is None or lprime < old:
                # journalise avant de modifier
                if vprime not in log_level:
                    log_level[vprime] = old
                L[vprime] = lprime
                heapq_heappush(Q, (lprime, vprime))

                # mise à jour cumulative
                s_v += (lprime - alpha_v)
                if (lprime - alpha_v) > delta_v:
                    delta_v = lprime - alpha_v

    return L, s_v, delta_v, log_level


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
    if not hasattr(G, "_neighbors_cache"):
        G._neighbors_cache = {u: list(G.successors(u)) if G.is_directed() else list(G.neighbors(u)) for u in G.nodes()}
        G._weights_cache = {(u, v): G[u][v].get('weight', 1.0) for u, v in G.edges()}
    V = len(G.nodes())
    V_hat, S_hat = prep(G)
    S = schedule(G, V_hat, S_hat)
    dead = set()
    for v in Start(S):
        #start_optimized = time.perf_counter()
        (L, s, delta_p) = PFS(G, v ,G._neighbors_cache)
        #end_optimized = time.perf_counter()
        #print(f"PFS Time: {end_optimized - start_optimized:.4f} seconds")
        process(G, v, L, s, A, S, k, V, delta_p, dead,neighbors_cache=G._neighbors_cache,weights_cache=G._weights_cache)  
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


def process(G, p, L, s, A, S, k, V, delta_p, dead,neighbors_cache,weights_cache):
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
    #start_optimized = time.perf_counter()
    prune(p, L, s, theta_A, S, delta_p, G,neighbors_cache,weights_cache)
    #end_optimized = time.perf_counter()
    #print(f"Prune Time: {end_optimized - start_optimized:.4f} seconds")
   

    # --- 3. Propagation à chaque successeur planifié
    for v in S.get(p, []):
        L, s2, delta_v, log_level = optimized_PFS(G, v, p, L, s, delta_p,neighbors_cache,weights_cache)
        process(G, v, L, s2, A, S, k, V, delta_v, dead,neighbors_cache,weights_cache)
        rollback(L, log_level)  # ✅ rollback sur la même référence
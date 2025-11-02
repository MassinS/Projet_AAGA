# ======================================
# Algorithm 1: Label-setting Fastest Paths
# (durées minimales temporelles depuis une source)
# ======================================

from dataclasses import dataclass
import heapq
from typing import Dict, List, Tuple, Any, Set
from temporal_graph import TemporalGraph



# Un label décrit "j'atteins v, en partant à s depuis la source, et en arrivant à a"
@dataclass
class Label:
    v: Any   # sommet d'arrivée
    s: float # start time (instant où le chemin depuis la source a effectivement commencé)
    a: float # arrival time (instant d'arrivée à v)

    @property   
    def duration(self) -> float:  # durée totale du trajet
        return self.a - self.s


def _is_dominated(new_label: Label, labels: List[Label]) -> bool:
    """
    Retourne True si new_label est dominé par un label déjà présent.
    Règle simple (suffisante ici) pour deux labels vers le même v :
      l1 domine l2 si:
        - l1.s >= l2.s et l1.a <= l2.a
        - et au moins une inégalité stricte
    Intuition: partir plus tard mais arriver plus tôt (ou égal) => meilleur.
    """
    for old in labels:
        if (old.s >= new_label.s and old.a <= new_label.a) and (old.s > new_label.s or old.a < new_label.a):
            return True
    return False

# D'après l'article de Wu et al. (2009) "Fastest Path Computation in Temporal Graphs" , les labels dominés par d'autre labels peuvent etre supprimé.
def _prune_dominated(labels: List[Label]) -> List[Label]:
    """
    Optionnel: supprime des labels qui sont dominés par d'autres dans la même liste.
    (petite passe de nettoyage pour garder la liste Π[v] "propre")
    """
    kept: List[Label] = []
    for l in labels:
        if not any(
            (k.s >= l.s and k.a <= l.a) and (k.s > l.s or k.a < l.a)  # k domine l
            for k in labels if k is not l
        ):
            kept.append(l)
    return kept


def fastest_paths(G, source: Any, interval: Tuple[float, float]) -> Dict[Any, float]:
    """
    Calcule, pour chaque sommet v, la durée minimale temporelle (fastest path)
    depuis 'source' dans l'intervalle I = [a, b].
 
    Paramètres
    ----------
    G : TemporalGraph
        Ton graphe temporel (voir temporal_graph.py), avec:
          - G.V : ensemble des sommets
          - G.get_out_edges(u, interval) : arêtes sortantes de u actives dans I
    source : Any
        Le sommet source.
    interval : (α, β)
        L'intervalle de temps considéré. Une arête (t, λ) est utilisable si α ≤ t ≤ β - λ.

    Retour
    ------
    d : dict[v -> float]
        Durée minimale (a - s) pour atteindre v depuis la source dans I.
        d[source] = 0. Les sommets inatteignables ont d[v] = +inf.
    """
    # La première étape consiste à initialiser les structures de données nécessaires.
    # d est un dictionnaire qui stocke la durée minimale pour atteindre chaque sommet depuis la source.
    # en début on mets tout les sommets à l'infini sauf la source qui est à 0.
    d: Dict[Any, float] = {v: float('inf') for v in G.V}
    d[source] = 0.0

    # 2) Labels stockés par sommet: Π[v] = liste de labels non dominés qui arrivent à v
    
    """
    Un sommet peut être atteint de plusieurs façons dans un graphe temporel (différents horaires, différents chemins).
    On veut donc garder une trace de toutes les façons d’arriver à ce nœud, mais seulement les meilleures (non dominées).

    """
    Π: Dict[Any, List[Label]] = {v: [] for v in G.V}

    # 3) File de priorité (tas) : on extrait toujours la plus petite durée en premier
    #    Chaque élément du tas: (duration, Label)
    Q: List[Tuple[float, Label]] = []
    # Label initial "fictif" sur la source : a=0, s=0 (durée 0)
    heapq.heappush(Q, (0.0, 0, Label(v=source, s=0.0, a=0.0)))

    # 4) Sommets "fixés" : dès qu'on sort le 1er label d'un v, d[v] est optimal
   
    F: Set[Any] = set()

    counter = 0

    # 5) Boucle principale
    while Q and len(F) < len(G.V):
        _, _, lab = heapq.heappop(Q)
        v, s, a = lab.v, lab.s, lab.a

        # Si v n'est pas encore "fixé", ce label donne sa durée minimale
        if v not in F:
            d[v] = a - s
            F.add(v)

            # Étendre le label via toutes les arêtes sortantes actives dans I
            for e in G.get_out_edges(v, interval):
                # Respect de la causalité: on ne peut emprunter e que si on est arrivé (a) avant son apparition (e.t)
                if a <= e.t:
                    # Si c'est le 1er vrai départ (label initial a=0,s=0), on "démarre" à e.t
                    s_prime = s if s != 0 else e.t
                    a_prime = e.t + e.l
                    new_lab = Label(v=e.v, s=s_prime, a=a_prime)

                    # Dominance: si un label existant vers e.v est meilleur, on ignore celui-ci
                    if not _is_dominated(new_lab, Π[e.v]):
                        Π[e.v].append(new_lab)
                        # Optionnel: "nettoyer" Π[e.v] pour ne garder que les meilleurs
                        Π[e.v] = _prune_dominated(Π[e.v])

                        counter += 1
                        heapq.heappush(Q, (new_lab.duration, counter, new_lab))


    return d


# --- TEST LOCAL ---
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

    # 2️⃣ Lancer l’algorithme depuis la source A
    interval = (0, 20)
    print(f"=== Fastest paths depuis 'A' dans l'intervalle {interval} ===")

    d = fastest_paths(G, source="A", interval=interval)

    # 3️⃣ Afficher les résultats
    for v in sorted(G.V):
        print(f"{v} : {d[v]}")

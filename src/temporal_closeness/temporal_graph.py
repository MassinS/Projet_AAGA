# ======================================
# Représentation du graphe temporel
# ======================================

from collections import defaultdict

# --- 1) Classe TemporalEdge ---
class TemporalEdge:
    def __init__(self, u, v, t, l):
        self.u = u
        self.v = v
        self.t = t
        self.l = l
    def __repr__(self):
        return f"({self.u}->{self.v}, t={self.t}, λ={self.l})"


# --- 2) Classe TemporalGraph ---
class TemporalGraph:
    def __init__(self):
        self.V = set() # pour stocker les sommets
        self.adj = defaultdict(list)  # pour stocker les arêtes sortantes de chaque sommet qui est un dictionnaire de listes.

    # Cette méthode permet d'ajouter une arête temporelle au graphe
    def add_edge(self, u, v, t, l):
        edge = TemporalEdge(u, v, t, l)
        self.V.update([u, v])
        self.adj[u].append(edge)

   # Cette méthode permet de récupérer les arêtes sortantes (avec filtre temporel)
    def get_out_edges(self, u, interval=None):
        # Sans intervalle, retourne toutes les arêtes sortantes de u
        if interval is None:
            return self.adj[u]
        # Avec intervalle, filtre les arêtes sortantes de u selon l'intervalle [α, β)
        a, b = interval
        return [e for e in self.adj[u] if a <= e.t <= b - e.l] # e.t >= α et e.t + e.l <= β 

    # Affiche chaque sommet source et la liste de ses arêtes sortantes formatées via TemporalEdge.__repr__.
    def __repr__(self):
        return "\n".join([f"{u}: {self.adj[u]}" for u in self.adj])


# --- 3 Tests pour vérifier la structure du graphe ---
if __name__ == "__main__":
    G = TemporalGraph()
    G.add_edge("A", "B", 1, 2)
    G.add_edge("B", "C", 3, 1)
    G.add_edge("A", "C", 5, 1)

    print("=== Graphe complet ===")
    print(G)

    print("\n=== Arêtes sortantes de A ===")
    print(G.get_out_edges("A"))

    print("\n=== Arêtes sortantes de A dans [0,4] ===")
    print(G.get_out_edges("A", (0,4)))

import osmnx as ox
import os
import networkx as nx
import matplotlib.pyplot as plt


def get_city_graph(city_name, network_type='drive', save_local=True):
    """
    Télécharge le graphe routier EXACT d'une ville, tel que défini dans OpenStreetMap.
    Aucune conversion, aucune simplification, aucun filtrage.
    On obtient un MultiDiGraph orienté avec sens uniques réels.
    """
    print(f"⏳ Téléchargement du graphe brut pour {city_name}...")
    
    # 1️⃣ Télécharger le graphe routier tel qu’il est dans OSM
    G = ox.graph_from_place(city_name, network_type='drive')
    # 2️⃣ Afficher quelques infos
    print(f"✅ Graphe téléchargé : {len(G.nodes())} nœuds, {len(G.edges())} arêtes")
    print(f"🔹 Type : {type(G)}")
    print(f"🔹 Dirigé ? {G.is_directed()}")
    
    return G



def plot_city_graph(G, city_name, top_nodes=None, mode="classic"):
    """
    Sauvegarde le graphe dans le dossier ../../graph/<mode>/
    Les 5 nœuds les plus centraux sont affichés en rouge.
    - mode="classic"  => graph/classic/
    - mode="efficient" => graph/efficient/
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'graph'))
    output_dir = os.path.join(base_dir, mode)
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{city_name.replace(',', '').replace(' ', '_')}_graph.png"
    output_path = os.path.join(output_dir, filename)

    fig, ax = ox.plot_graph(
        G,
        node_color='lightgray',
        edge_color='gray',
        node_size=5,
        show=False,
        close=False
    )

    if top_nodes:
        node_positions = {n: (data['x'], data['y']) for n, data in G.nodes(data=True)}
        x_top = [node_positions[n][0] for n in top_nodes]
        y_top = [node_positions[n][1] for n in top_nodes]
        ax.scatter(x_top, y_top, c='red', s=30, label='Top closeness')
        plt.legend()

    plt.title(f"Graphe routier de {city_name}")
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"🖼️  Graphe sauvegardé dans : {output_path}")

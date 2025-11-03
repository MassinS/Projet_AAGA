import osmnx as ox
import os
import networkx as nx
import matplotlib.pyplot as plt


def get_city_graph(city_name, network_type='drive', save_local=True):
    """
    Télécharge le graphe d'une ville via OSMnx, ou le charge depuis un fichier si déjà sauvegardé.
    Les fichiers .graphml sont enregistrés dans ../../data
    """
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))
    os.makedirs(data_dir, exist_ok=True)

    filename = city_name.replace(',', '').replace(' ', '_') + '.graphml'
    file_path = os.path.join(data_dir, filename)

    if save_local and os.path.exists(file_path):
        print(f"📂 Chargement du graphe local : {file_path}")
        G = ox.load_graphml(file_path)
        return G

    print(f"⏳ Téléchargement du graphe pour {city_name}...")
    G = ox.graph_from_place(city_name, network_type=network_type)
    G = G.to_undirected()

    if save_local:
        ox.save_graphml(G, file_path)
        print(f"💾 Graphe sauvegardé dans {file_path}")

    print(f"✅ Graphe téléchargé : {len(G.nodes)} nœuds, {len(G.edges)} arêtes")
    return G


def get_oriented_city_graph(city_name, save_local=True):
    """
    Télécharge ou charge un graphe routier orienté (MultiDiGraph) d'une ville.
    Les fichiers sont enregistrés dans ../../data
    """
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))
    os.makedirs(data_dir, exist_ok=True)

    filename = city_name.replace(',', '').replace(' ', '_') + '_oriented.graphml'
    file_path = os.path.join(data_dir, filename)

    if save_local and os.path.exists(file_path):
        print(f"📂 Chargement du graphe orienté local : {file_path}")
        G = ox.load_graphml(file_path)
    else:
        print(f"⏳ Téléchargement du graphe orienté pour {city_name}...")
        G = ox.graph_from_place(city_name, network_type='drive')

        print("🔍 Extraction de la plus grande composante fortement connexe...")
        if not nx.is_strongly_connected(G):
            largest_cc = max(nx.strongly_connected_components(G), key=len)
            G = G.subgraph(largest_cc).copy()
            print(f"✅ Graphe réduit à {len(G.nodes())} sommets et {len(G.edges())} arêtes")

        if save_local:
            ox.save_graphml(G, file_path)
            print(f"💾 Graphe orienté sauvegardé dans : {file_path}")

    print(f"✅ Graphe orienté prêt : {len(G.nodes())} sommets, {len(G.edges())} arêtes")
    print(f"🔹 Type : {'dirigé' if G.is_directed() else 'non dirigé'}")
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

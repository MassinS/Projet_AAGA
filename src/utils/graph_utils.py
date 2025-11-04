import osmnx as ox
import os
import networkx as nx
import matplotlib.pyplot as plt


def get_city_graph(city_name, network_type='drive', save_local=True):
    """
    Télécharge le graphe d'une ville via OSMnx, ou le charge depuis un fichier si déjà sauvegardé.
    Les fichiers .graphml sont enregistrés dans ../../data
    """
    

    print(f"⏳ Téléchargement du graphe pour {city_name}...")
    G = ox.graph_from_place(city_name, network_type=network_type)
    G = G.to_undirected()

    if save_local:
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))
        os.makedirs(data_dir, exist_ok=True)

        filename = city_name.replace(',', '').replace(' ', '_') + '.graphml'
        file_path = os.path.join(data_dir, filename)
        
        ox.save_graphml(G, file_path)
        print(f"💾 Graphe sauvegardé dans {file_path}")

    print(f"✅ Graphe téléchargé : {len(G.nodes)} nœuds, {len(G.edges)} arêtes")
    return G


def get_oriented_city_graph(city_name, network_type='drive', save_local=True):
    """
    Télécharge le graphe routier EXACT d'une ville depuis OpenStreetMap
    et le sauvegarde dans le dossier data/ sous forme de fichier .graphml.

    Args:
        city_name (str): Nom complet de la ville (ex: "Paris, France")
        network_type (str): Type de réseau (par défaut 'drive')
        save_local (bool): Si True, sauvegarde le graphe dans data/

    Returns:
        G (networkx.MultiDiGraph): Graphe orienté de la ville
    """
    print(f"⏳ Téléchargement du graphe brut pour {city_name}...")

    # 1️⃣ Télécharger le graphe routier
    G = ox.graph_from_place(city_name, network_type=network_type)

    # 2️⃣ Sauvegarder localement dans le dossier data/
    if save_local:
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))
        os.makedirs(data_dir, exist_ok=True)

        # Nom de fichier propre : ex "Paris_France.graphml"
        filename = city_name.replace(", ", "_").replace(" ", "_") + ".graphml"
        path = os.path.join(data_dir, filename)

        ox.save_graphml(G, path)
        print(f"💾 Graphe sauvegardé dans : {path}")

    return G

def plot_city_graph(G, city_name, top_nodes=None, mode="classic"):
    """
    Sauvegarde le graphe dans le dossier ../../visualisation/<mode>/
    Les 5 nœuds les plus centraux sont affichés en rouge.
    - mode="classic"  => visualisation/classic/
    - mode="efficient" => visualisation/efficient/
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'visualisation'))
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

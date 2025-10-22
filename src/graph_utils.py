import osmnx as ox
import os
import networkx as nx
import matplotlib.pyplot as plt

def get_city_graph(city_name, network_type='drive', save_local=True):
    """
    Télécharge le graphe d'une ville via OSMnx, ou le charge depuis un fichier si déjà sauvegardé.
    """
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    filename = city_name.replace(',', '').replace(' ', '_') + '.graphml'
    file_path = os.path.join(data_dir, filename)

    # Si le graphe est déjà sauvegardé, on le recharge directement
    if save_local and os.path.exists(file_path):
        print(f"📂 Chargement du graphe local : {file_path}")
        G = ox.load_graphml(file_path)
        return G

    # Sinon, on le télécharge depuis OSM
    print(f"⏳ Téléchargement du graphe pour {city_name}...")
    G = ox.graph_from_place(city_name, network_type=network_type)
    G = G.to_undirected()

    # On le sauvegarde localement
    if save_local:
        ox.save_graphml(G, file_path)
        print(f"💾 Graphe sauvegardé dans {file_path}")

    print(f"✅ Graphe téléchargé : {len(G.nodes)} nœuds, {len(G.edges)} arêtes")
    return G



def plot_city_graph(G, city_name, top_nodes=None):
    """
    Sauvegarde le graphe dans le dossier ../graph/
    Les 5 nœuds les plus centraux sont affichés en rouge.
    """
    # Dossier de sortie (en dehors de src)
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'graph')
    os.makedirs(output_dir, exist_ok=True)

    # Nom du fichier image
    filename = f"{city_name.replace(',', '').replace(' ', '_')}_graph.png"
    output_path = os.path.join(output_dir, filename)

    # Création du graphique
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

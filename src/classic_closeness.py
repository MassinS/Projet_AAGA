import networkx as nx
from collections import deque

def closeness_centrality_all_nodes(G):
    """
    Compute closeness centrality for all nodes in an unweighted, undirected graph.
    Based on Algorithm 1 from the course.
    """
    closeness = {}
    
    for v in G.nodes():
        # Step 1: initialize distances
        dist = {u: float('inf') for u in G.nodes()}
        dist[v] = 0
        
        # Step 2: initialize queue and BFS
        Q = deque([v])
        
        while Q:
            x = Q.popleft()
            for y in G.neighbors(x):
                if dist[y] == float('inf'):  # not visited yet
                    dist[y] = dist[x] + 1
                    Q.append(y)
        
        # Step 3: compute sum of distances
        S = sum(dist[u] for u in G.nodes() if u != v and dist[u] < float('inf'))
        
        # Step 4: compute closeness
        if S > 0:
            closeness[v] = 1 / S
        else:
            closeness[v] = 0.0  # isolated node
        
    return closeness

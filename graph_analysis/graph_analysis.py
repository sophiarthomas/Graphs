import networkx as nx
import matplotlib.pyplot as plt
import argparse
import os
import numpy as np

### UTIL 

def betweenness(G, n):
    """Partition the graph into n components by removing high betweenness edges."""
    components = list(nx.connected_components(G))
    num_components = len(components)

    if num_components >= n:
        print(f"Error: Graph already has {num_components} components, cannot partition further.")
        return None
    
    while num_components < n:
        btwn = nx.edge_betweenness_centrality(G)  # Use EDGE betweenness
        if not btwn:
            break
        
        max_edge = max(btwn, key=btwn.get)  # Find the highest betweenness edge
        print(f"Removing edge: {max_edge} (Betweenness: {btwn[max_edge]:.4f})")
        G.remove_edge(*max_edge)  

        components = list(nx.connected_components(G))
        num_components = len(components)

    return G

def bfs(G, start_node):
    """BFS function to get BFS nodes and edges starting from a node."""
    bfs_edges = list(nx.bfs_edges(G, source=start_node))
    bfs_nodes = {start_node} | {v for u, v in bfs_edges}
    return bfs_nodes, bfs_edges

def compute_neighborhood_overlap(G):
    """Compute the neighborhood overlap for each edge."""
    overlap = {}
    for u, v in G.edges():
        neighbors_u = set(G.neighbors(u))
        neighbors_v = set(G.neighbors(v))
        intersection_size = len(neighbors_u & neighbors_v)
        union_size = len(neighbors_u | neighbors_v)
        overlap[(u, v)] = intersection_size / union_size if union_size > 0 else 0
    return overlap

def on_click(event, G, state):
    """Mouse click event handler for interactive BFS and graph toggling. Used for plotting neighborhood overlap """
    if event.inaxes is None:
        return

    x_clicked, y_clicked = event.xdata, event.ydata
    pos = nx.spring_layout(G, seed=42)

    # Find the closest node to the clicked point
    closest_node = None
    min_distance = float('inf')

    # Check the distance to all nodes to find the closest one
    if state[3] is True:  # BFS is active, check within BFS subgraph
        for node in state[5].nodes:
            x_node, y_node = state[0][node]  # Get the position of the node
            distance = (x_node - x_clicked) ** 2 + (y_node - y_clicked) ** 2
            if distance < min_distance:
                min_distance = distance
                closest_node = node
    else:  # No BFS, check within the original graph
        for node in G.nodes:
            x_node, y_node = pos[node]  # Get the position of the node
            distance = (x_node - x_clicked) ** 2 + (y_node - y_clicked) ** 2
            if distance < min_distance:
                min_distance = distance
                closest_node = node

    # Define a threshold to check if the click is near a node
    distance_threshold = 0.1  

    # If no node is close enough, do nothing
    if min_distance > distance_threshold:
        closest_node = None
        state[3] = True # Simulating active bfs to ensure that the og graph stays 

    if state[3]:
        # If bfs was active, revert to the original graph
        state[3] = False
        state[4] = None
        plot_neighborhood_overlap(G, state)  # Reset to neighborhood overlap graph
    else:
        # Perform BFS on the clicked node
        state[3] = True
        state[4] = closest_node
        plot_bfs_graph(G, closest_node, state)

### PLOTTING

def plot_graph(G, plot_types):
    """Plot the graph based on selected options (C, N, P)."""
    valid_args = {'C': False, 'N': False, 'P': False}
    for char in plot_types:
        if char in valid_args:
            valid_args[char] = True
        else:
            print(f"Invalid plot option: {char}")
            return

    # Check which argument to apply 
    if valid_args['C']:
        clustering_coeffs = nx.clustering(G)
        plot_clustering(G, clustering_coeffs)
        
    if valid_args['N']:
        """Plot the graph highlighting neighborhood overlap, interactive BFS on click."""
        pos = nx.spring_layout(G, seed=42)
        fig, ax = plt.subplots()
        bfs_active = False # Track bfs state
        selected_node = None # Track selected Node 
        state = [pos, fig, ax, bfs_active, selected_node, G]

        ax.clear()
        plot_neighborhood_overlap(G, state)
        ax.set_title("Neighborhood Overlap Graph")

        fig.canvas.mpl_connect("button_press_event", lambda event: on_click(event, G,  state)) # Connect event listener
   
    if valid_args['P']:
        plot_attributes(G)

    plt.show()

def plot_attributes(G):
    """Color nodes based on attributes if assigned, otherwise default gray."""
    colors = []
    for node in G.nodes():
        colors.append(G.nodes[node].get("color", "gray"))

    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G, seed=42)
    plt.title("Graph Colored by Attributes (Default: Gray)")
    nx.draw(G, pos, with_labels=True, node_color=colors, edge_color="gray", font_size=8)
    
def plot_clustering(G, clustering_coeffs):
    """Visualize clustering coefficients using node size and color."""
    cluster_min = min(clustering_coeffs.values())
    cluster_max = max(clustering_coeffs.values()) or 1  # Avoid division by zero

    node_sizes = {
        v: 100 + ((clustering_coeffs[v] - cluster_min) / (cluster_max - cluster_min)) * (800 - 100)
        for v in G.nodes()
    }

    degrees = dict(G.degree())
    max_degree = max(degrees.values()) or 1  # Avoid division by zero

    node_colors = [(254 * (degrees[v] / max_degree), 0, 254) for v in G.nodes()]
    node_colors = np.array(node_colors) / 255.0  # Normalize colors

    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42)
    plt.title("Clustering Coefficients")
    nx.draw(G, pos, with_labels=True, node_size=[node_sizes[v] for v in G.nodes()], 
            node_color=node_colors, edge_color="gray", font_size=8)

def plot_neighborhood_overlap(G, state):
    """Plot the graph highlighting neighborhood overlap."""
    plt.clf()
    state[2].clear()
    pos = nx.spring_layout(G, seed=42)  # Positioning for the graph

    overlap = compute_neighborhood_overlap(G)

    edge_colors = [overlap[edge] for edge in G.edges()]

    plt.title("Graph Highlighting Neighborhood Overlap")
    nx.draw(G, pos, with_labels=True, edge_color=edge_colors, edge_cmap=plt.cm.plasma,
            node_color="lightblue", font_size=8)
    plt.draw()

def plot_bfs_graph(G, start_node, state):
    """Draw the BFS graph starting from a selected node."""
    plt.clf()
    state[2].clear()
    state[2].set_title(f"BFS from {start_node}")

    bfs_nodes, bfs_edges = bfs(G, start_node)
    levels = {start_node: 0}

    for node in bfs_nodes:
        level = nx.shortest_path_length(G, source=start_node, target=node)
        levels[node] = level

    state[5] = G.edge_subgraph(bfs_edges).copy()

    state[0] = nx.spring_layout(state[5], seed=42)
    new_pos = {node: (state[0][node][0], -levels[node]) for node in levels}

    plt.title(f"BFS Graph of node {start_node}")
    nx.draw(state[5], pos=new_pos, with_labels=True, node_color="lightblue", edge_color="black", 
            node_size=500, font_size=8, font_weight="bold", alpha=0.7)
    plt.draw()

### VERIFYING

def verify_homophily(G):
    """Verifies homophily by calculating the proportion of mixed edges."""
    color_counts = {"r": 0, "g": 0}
    for node in G.nodes:
        color = G.nodes[node].get("color", None)
        if color in color_counts:
            color_counts[color] += 1

    total_nodes = sum(color_counts.values())
    if total_nodes == 0:
        raise ValueError("Graph has no node color attributes.")

    p = color_counts["r"] / total_nodes
    q = color_counts["g"] / total_nodes
    mixed_edge_p = 2 * p * q

    mixed_edges = sum(1 for s, t in G.edges if G.nodes[s]['color'] != G.nodes[t]['color'])
    percentage_me = mixed_edges / len(G.edges)

    return percentage_me <= mixed_edge_p  # Returns True if homophilic

def verify_balanced_graph(G) :
    """
    Check if a graph is structurally balanced based on node attributes and edge signs
    Param: 
        G (networkx.Graph)
    Returns: 
        bool: True if the graph is balanced, false otherwise 
    """ 
    cycles = nx.cycle_basis(G)

    for cycle in cycles: 
        negative_edges= 0

        for i in range(len(cycle)):
            u, v = cycle[i], cycle[(i+1) % len(cycle)]
            sign = G.edges.get((u,v), {}).get("sign", G.edges.get((v, u), {}).get("sign", "+"))

            if sign == "-": 
                negative_edges += 1

        if negative_edges % 2 == 1:   
            print(f"Unbalanced Graph: {cycle} with {negative_edges} negative edges")
            return False
    
    print("Graph is structurally balanced!")
    return True 

### MAIN FUNTION

def main():
    """Parse command-line arguments and execute graph analysis."""
    parser = argparse.ArgumentParser(description="Graph Analysis")
    parser.add_argument("filename", type=str, help="GML file to read graph data.")
    parser.add_argument("--components", type=int, help="Partition the graph into n components")
    parser.add_argument("--plot", type=str, help="Plot the graph highlighting [C|N|P]")
    parser.add_argument("--verify_homophily", action="store_true", help="Test for homophily")
    parser.add_argument("--verify_balanced_graph", action="store_true", help="Test for balanced graph")
    parser.add_argument("--output", type=str, help="Save the updated graph as a GML file")

    args = parser.parse_args()
    
    if not os.path.exists(args.filename):
        print(f"Error: File {args.filename} not found.")
        return
    
    G = nx.read_gml(args.filename)

    if args.components:
        G = betweenness(G, args.components)

    if args.verify_homophily:
        print(f"Homophily: {verify_homophily(G)}")

    if args.verify_balanced_graph: 
        print(f"Balanced Graph: {verify_balanced_graph(G)}")

    if args.plot:
        plot_graph(G, args.plot)

    if args.output:
        nx.write_gml(G, args.output)
        print(f"Updated graph saved to {args.output}")

if __name__ == "__main__":
    main()


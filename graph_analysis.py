import networkx as nx
import matplotlib.pyplot as plt
import argparse
import os
import numpy as np

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

def plot_graph(G, plot_types):
    """Plot the graph based on selected options (C, N, P)."""
    valid_args = {'C': False, 'N': False, 'P': False}
    for char in plot_types:
        if char in valid_args:
            valid_args[char] = True
        else:
            print(f"Invalid plot option: {char}")
            return

    if valid_args['C']:
        clustering_coeffs = nx.clustering(G)
        plot_clustering(G, clustering_coeffs)
        
    if valid_args['N']:
        plot_neighborhood_overlap(G)
        
    if valid_args['P']:
        plot_attributes(G)

    plt.show()

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
    nx.draw(G, pos, with_labels=True, node_size=[node_sizes[v] for v in G.nodes()], 
            node_color=node_colors, edge_color="gray", font_size=8)

def plot_neighborhood_overlap(G, bfs_root=None):
    """Plot the graph highlighting neighborhood overlap, interactive BFS on click."""
    plt.clf()
    pos = nx.spring_layout(G, seed=42)

    if bfs_root is None:
        overlap = compute_neighborhood_overlap(G)
        edge_colors = [overlap[edge] for edge in G.edges()]
        nx.draw(G, pos, with_labels=True, edge_color=edge_colors, edge_cmap=plt.cm.plasma, node_color="lightblue")
        plt.title("Graph Highlighting Neighborhood Overlap")
    else:
        bfs_edges = list(nx.bfs_edges(G, bfs_root))
        bfs_nodes = {bfs_root} | {v for _, v in bfs_edges}
        nx.draw(G, pos, with_labels=True,
                node_color=["red" if n in bfs_nodes else "gray" for n in G.nodes()],
                edge_color=["black" if (u, v) in bfs_edges else "gray" for u, v in G.edges()])
        plt.title(f"BFS from Node {bfs_root} (Click to Reset)")

    plt.draw()

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

def plot_attributes(G):
    """Color nodes based on attributes if assigned, otherwise default gray."""
    colors = []
    for node in G.nodes():
        colors.append(G.nodes[node].get("color", "gray"))

    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=True, node_color=colors, edge_color="gray", font_size=8)
    plt.title("Graph Colored by Attributes")

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

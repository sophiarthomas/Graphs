import networkx as nx
import matplotlib.pyplot as plt
import argparse
import os
import math
import numpy as np

def betweenness(G, n):
    """
    Calculates the betweenness and separates the graph into n components
    param: @G=graph, n=desired components
    returns: @dict
    """
    components = list(nx.connected_components(G))
    num_components = len(components)

    # Verify there are less than n components in the Graph 
    if num_components >= n:     
        print(f"Error: there are {num_components} in the graph, more than or equal to the requested {n} components.")
        return None
    
    # Remove edges until there are n components
    while num_components < n: 
        btwn = nx.betweenness_centrality(G)
    
        max_node = max(btwn, key=btwn.get)
        print(f"Node with highest betweenness: {max_node} (Score: {btwn[max_node]:.4f})")
        
        # Find the edge with the highest betweenness node
        if G.degree[max_node] > 0:
            max_edge = max(G.edges(max_node), key=lambda edge: btwn[edge[1]])
            print(f"Removing edge: {max_edge}")
            G.remove_edge(*max_edge)  # Remove only the edge, not the node
        
        components = list(nx.connected_components(G))
        num_components = len(components)

    return G

def plot_graph(G, args):
    """

    """
    # Ensuring the plot arg contains the correct values [C|N|P]
    valid_args = {'C': 0, 'N': 0, 'P': 0}
    for char in args: 
        if  char in valid_args:
            valid_args[char] = 1
        else: 
            return f"invalid argument: {char}"
        

    if valid_args['C'] == 1:
        clustering_coeffs = nx.clustering(G)
        plot_cc(G, clustering_coeffs)
        
        
    if valid_args['N'] == 1: 
        pass
    if valid_args['P'] == 1: 
        pass 

    plt.show()


def plot_cc(G, clustering_coeffs): 
    """
    
    """
     # Normalize clustering coefficients for node size
    cluster_min = min(clustering_coeffs.values())
    cluster_max = max(clustering_coeffs.values())
    
    if cluster_max - cluster_min == 0:  # Avoid division by zero
        cluster_max += 1e-6

    node_sizes = {
        v: 100 + ((clustering_coeffs[v] - cluster_min) / (cluster_max - cluster_min)) * (800 - 100)
        for v in G.nodes()
    }

    # Compute node degrees for color mapping
    degrees = dict(G.degree())
    max_degree = max(degrees.values()) if degrees else 1  # Avoid division by zero

    node_colors = [
        (254 * (degrees[v] / max_degree), 0, 254) for v in G.nodes()
    ]

    # Convert RGB to Matplotlib color format (values between 0 and 1)
    node_colors = np.array(node_colors) / 255.0

     # Draw the graph
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42)  # Positioning for visualization
    nx.draw(G, pos, with_labels=True, node_size=[node_sizes[v] for v in G.nodes()], 
            node_color=node_colors, edge_color="gray", font_size=8)
    
def plot_no(G):
    """ 
    Plot the graph highlighting neighborhood overlap 
    (Measures how much overlap there is between neighborhoods of adjacent nodes). 
    Plot must be interactive. When the user clicks on a node u, it displays the BFS with u as the root. 
    Then when the user clicks it plots the original graph.
    """
    pass
    

def verify_homophily(G):
    """
    
    """
    if (): 
        return False 
    else: 
        return True 
    
def verify_balance(G):
    """
    
    """
    return False





def main(): 
    """
    Parse through the argments to return the desired graph anaysis results 
    
    ex: python ./graph_analysis.py graph_file.gml --components n --plot [C|N|P] 
        --verify_homophily --verify_balanced_graph --output out_graph_file.gml

    """
    parser = argparse.ArgumentParser(description="Social and Large - Scale Networks")
    parser.add_argument("filename", type=str, help="GML file to read graph data. NOTE: graph nodes must have attributes")
    parser.add_argument("--component", nargs=1, type=int, help="Split the graph into n components")
    parser.add_argument("--plot", nargs='+', type=str, help="Plot the graph, Highlighting ") # OR nargs=*
    parser.add_argument("--verify_homophily", action='store_true', help="Tests for homophily in the graph based on the assigned node colors using the Student t-test")
    parser.add_argument("--verify_balanced_graph", action='store_true', help="Check if the graph is balanced based on the assigned edge signs")
    parser.add_argument("--output", type=str, help="Output file to save the updated graph in GML format")

    args = parser.parse_args()
    G = None

    # Check for arg filename
    if not args.filename: 
        print("Error: Must specify filename")
        return
    else: 
        if not os.path.exists(args.filename): 
            print(f"Error: File {args.filename} not found")
            return
        G = nx.read_gml(args.filename)

    # Check for arg --component n 
    if args.component:
        print(args.component[0])
        n = args.component[0]
        betweenness(G, n)

    # Check for arg --verify_homophily
    if args.verify_homophily: 
        print(f"Homophily: {verify_homophily(G)}")

    # Check for arg --verify_balanced_graph
    if args.verify_balanced_graph: 
        print(f"Balanced Graph: {verify_balance(G)}")

    # Check for arg --plot 
    if args.plot: 
        plot_graph(G, args.plot[0])

    # Check for arg --output 
    if args.output: 
        nx.write_gml(G, args.output)
        print(f"Updated graph saved to {args.output}")


if __name__ == "__main__":
    main()
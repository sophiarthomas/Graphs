import networkx as nx
import matplotlib.pyplot as plt
import argparse
import os
import math

def betweenness(G, n):
    """
    Calculates the betweenness and separates the graph into n components
    param @G=graph, n=desired components
    returns @dict
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





def main(): 
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

    if args.component:
        print(args.component[0])
        n = args.component[0]
        betweenness(G, n)

    # Check for arg --output 
    if args.output: 
        nx.write_gml(G, args.output)
        print(f"Updated graph saved to {args.output}")


if __name__ == "__main__":
    main()
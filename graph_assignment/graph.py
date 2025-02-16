import networkx as nx
import matplotlib.pyplot as plt
import argparse
import os
import math

def generate_random_graph(n, c):
    p = (c * math.log(n)) / n  # Edge probability
    G = nx.erdos_renyi_graph(n, p, seed=None)
    
    # Relabel nodes as strings
    mapping = {i: str(i) for i in range(n)}
    G = nx.relabel_nodes(G, mapping)
    return G 


def bfs_hierarchy_layout(G, start_node):
    """Generates a hierarchical layout for BFS visualization."""
    levels = {}  # Stores nodes by their BFS depth/length
    pos = {}     # Stores (x, y) positions of nodes
    
    for node, depth in nx.single_source_shortest_path_length(G, start_node).items():
        levels.setdefault(depth, []).append(node)
    
    max_width = max(len(nodes) for nodes in levels.values())  # Max nodes in a level

    # Assign positions
    for depth, nodes in levels.items():
        num_nodes = len(nodes)
        spacing = max_width / (num_nodes + 1)
        for i, node in enumerate(nodes):
            pos[node] = (i * spacing, -depth)  # Arrange nodes downward by level

    # Ensure all nodes have a position 
    for node in G.nodes(): 
        if node not in pos:
            pos[node] = (5, 0)
    
    return pos

def bfs(G, start_node):
    if start_node not in G: 
        print(f"Error: Node {start_node} not found in graph.")
        return {}
    return nx.bfs_tree(G, start_node)


def plot_graph(G, bfs_tree, start_node):
    """Plots the graph. If BFS is given, highlights it."""
    plt.figure(figsize=(12, 8))
    if bfs_tree: 
        pos = bfs_hierarchy_layout(G, start_node)
    else: 
        pos = nx.spring_layout(G, k=10.0 / (len(G.nodes) ** 0.5), seed=42)
    

    # Draw edges
    nx.draw(G, pos, with_labels=False, node_size=400, node_color="lightgray", edge_color="gray", alpha=0.3)
    
    # Highlight BFS if provided
    if bfs_tree:
        nx.draw_networkx_edges(G, pos, edgelist=bfs_tree.edges(), edge_color="blue", width=2)
        nx.draw_networkx_nodes(G, pos, nodelist=bfs_tree.nodes(), node_color="royalblue", edgecolors="black", node_size=600)
        title = "Graph with BFS Highlighted"
    else:
        nx.draw_networkx_nodes(G, pos, node_color="lightblue", edgecolors="black", node_size=500)
        title = "Plotted Graph"

    labels = {node: node for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight="bold", font_color="black")    
    plt.title(title)
    plt.axis("off")
    plt.show()


def main(): 
    parser = argparse.ArgumentParser(description="Erdos-Renyi Random Graph")
    # Attaching argument specifications to the parser 
    parser.add_argument("--input", type=str, help="Input GML file to read graph data")
    parser.add_argument("--create_random_graph", nargs=2, type=float , metavar=('n', 'c'), help="Generate a random graph based on number and constant")
    parser.add_argument("--BFS", type=str, help="Compute BFS shortest paths from a given node and highlight on visual")
    parser.add_argument("--plot", action='store_true', help="Plot the graph")
    parser.add_argument("--output", type=str, help="Output file to save the graph in GML format")

    args = parser.parse_args()
    G = None

    # Check for arg --input and/or --create_random_graph 
    if args.input: 
        if not os.path.exists(args.input): 
            print(f"Error: File {args.input} not found")
            return
        G = nx.read_gml(args.input)
    elif args.create_random_graph: 
        n, c = int(args.create_random_graph[0]), float(args.create_random_graph[1])
        G = generate_random_graph(n, c)
    else: 
        print("Error: Must specify either --input or --create_random_graph.")
        return
    
    # Check for arg --BFS and --plot 
    bfs_tree = None
    if args.BFS:
        bfs_tree = bfs(G, args.BFS)

    if args.plot or bfs_tree:
        plot_graph(G, bfs_tree, args.BFS)

    # Check for arg --output 
    if args.output: 
        nx.write_gml(G, args.output)
        print(f"Graph saved to {args.output}")


if __name__ == "__main__": 
    main()

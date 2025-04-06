import argparse
import os
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

"""
--plot 
--interactive

## --interactive

Requests that the program show the output of every round graph. 
A round is defined as obtaining the preference SELLER graph, 
compute the CONSTRICTED sets via matching, and UPDATE the valuation.
"""
def load_graph(gml_file):
    """Load a bipartite graph from a GML file."""
    if not os.path.exists(gml_file):
        raise FileNotFoundError(f"Error: File {gml_file} not found.")
    G = nx.read_gml(gml_file)
    return G

def compute_preferred_seller_graph(G):
    """Compute the preferred-seller graph based on valuations and prices."""
    preferred_graph = nx.Graph()
    buyers = [n for n in G.nodes if G.nodes[n]['bipartite'] == 1]
    sellers = [n for n in G.nodes if G.nodes[n]['bipartite'] == 0]
    
    for buyer in buyers:
        best_seller = None
        best_value = -float('inf')
        
        for seller in sellers:
            if G.has_edge(seller, buyer):
                valuation = G[seller][buyer]['valuation']
                price = G.nodes[seller]['price']
                payoff = valuation - price
                
                if payoff > best_value:
                    best_value = payoff
                    best_seller = seller
        
        if best_seller is not None:
            preferred_graph.add_edge(best_seller, buyer)
    
    return preferred_graph

def interactive_market_clearing(G):
    round_counter = 1
    while True:
        print(f"\n=== Round {round_counter} ===")

        # 1. Build preferred seller graph
        preferred_graph = compute_preferred_seller_graph(G)

        # 2. Compute matching
        buyers = [n for n in G.nodes if G.nodes[n]['bipartite'] == 1]
        sellers = [n for n in G.nodes if G.nodes[n]['bipartite'] == 0]
        matching = nx.bipartite.maximum_matching(preferred_graph, top_nodes=buyers)
        matched_buyers = set(matching.keys()) & set(buyers)
        all_buyers = set(buyers)

        # 3. Check for perfect matching
        if matched_buyers == all_buyers:
            print("Market cleared with perfect matching!")
            plot_matching(preferred_graph, matching, title=f"Perfect Matching - Round {round_counter}")
            break

        # 4. Identify constricted sets
        unmatched_buyers = all_buyers - matched_buyers
        constricted_sellers = set()
        for buyer in unmatched_buyers:
            neighbors = list(preferred_graph.neighbors(buyer))
            constricted_sellers.update(neighbors)

        # 5. Visualize phases
        print("1: Preferred Seller Graph")
        plot_graph_with_highlights(preferred_graph, highlight_nodes=unmatched_buyers, title=f"Preferred Seller Graph - Round {round_counter}")

        print("2: Matching")
        plot_matching(preferred_graph, matching, title=f"Matching - Round {round_counter}")

        print("3: Constricted Set")
        plot_graph_with_highlights(
            preferred_graph,
            highlight_nodes=constricted_sellers,
            node_color='orange',
            title=f"Constricted Set - Sellers to Update - Round {round_counter}"
        )

        # 6. Update prices of sellers in constricted set
        for seller in constricted_sellers:
            G.nodes[seller]['price'] += 1
            print(f"Updated price of seller {seller} to {G.nodes[seller]['price']}")

        input("Press Enter to continue to the next round...")
        round_counter += 1

def plot_graph_with_highlights(G, highlight_nodes=None, node_color='red', title=""):
    pos = nx.spring_layout(G, seed=42)
    node_colors = ['lightblue' if n not in highlight_nodes else node_color for n in G.nodes]

    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_color=node_colors, edge_color='gray', node_size=2000)
    plt.title(title)
    plt.show()

def plot_matching(G, matching, title="Matching"):
    pos = nx.spring_layout(G, seed=42)
    matching_edges = [(u, v) for u, v in matching.items() if (u, v) in G.edges or (v, u) in G.edges]

    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_color='lightgreen', edge_color='gray', node_size=2000)
    nx.draw_networkx_edges(G, pos, edgelist=matching_edges, edge_color='blue', width=2)
    plt.title(title)
    plt.show()

def plot_graph(G):
    from networkx.algorithms import bipartite

    buyers = [n for n in G.nodes if G.nodes[n].get('bipartite') == 1]
    sellers = [n for n in G.nodes if G.nodes[n].get('bipartite') == 0]

    # Assign colors by type
    node_colors = []
    node_labels = {}
    for node in G.nodes:
        if node in sellers:
            node_colors.append("lightcoral")
            node_labels[node] = f"{node}\nP: {G.nodes[node].get('price', 0)}"
        else:
            node_colors.append("skyblue")
            node_labels[node] = str(node)

    pos = nx.bipartite_layout(G, sellers)

    edge_labels = {(u, v): G[u][v].get('valuation', '') for u, v in G.edges}

    plt.figure(figsize=(10, 6))
    nx.draw(G, pos, with_labels=True, labels=node_labels,
            node_color=node_colors, edge_color='gray', node_size=2000, font_size=10)

    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='black')

    plt.title("Bipartite Market Graph with Valuations and Prices")
    plt.axis('off')
    plt.show()


def main(): 
    """Parse command-line arguments and execute graph analysis."""
    parser = argparse.ArgumentParser(description="Traffic Equilibrium and Social Optimality Calculator")
    parser.add_argument("gml_file", type=str, help="Path to the directed graph file in .gml format")
    parser.add_argument("--plot", action="store_true", help="Plot the biparte graph")
    parser.add_argument("--interactive", action="store_true", help="Show the output of every round graph (Preference seller graph)")

    args = parser.parse_args()
    G = load_graph(args.gml_file)
    if G is None:
        print("Error loading graph.")
        return

    if args.plot:
        plot_graph(G)
        print("Graph plotted.")

    if args.interactive:
        interactive_market_clearing(G)


if __name__ == '__main__': 
    main()
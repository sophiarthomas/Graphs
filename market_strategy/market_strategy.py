import argparse
import os
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import math 
import copy 

def load_graph(gml_file):
    """Load a bipartite graph from a GML file."""
    if not os.path.exists(gml_file):
        raise FileNotFoundError(f"Error: File {gml_file} not found.")
    G = nx.read_gml(gml_file)
    return G

def interactive_mode(G):
    from networkx.algorithms import bipartite

    def compute_preference_graph(G, prices):
        pref_G = nx.Graph()
        preferred_sellers = {}

        for buyer in buyers:
            max_payoff = float('-inf')
            best_sellers = []

            for neighbor in G.neighbors(buyer):
                seller = neighbor
                valuation = G[seller][buyer].get('valuation', 0)
                price = prices.get(seller, 0)
                payoff = valuation - price

                G[seller][buyer]['payoff'] = payoff  

                if payoff > max_payoff:
                    max_payoff = payoff
                    best_sellers = [seller]
                elif payoff == max_payoff:
                    best_sellers.append(seller)

            # Only include preferred edges in preference graph
            preferred_sellers[buyer] = best_sellers
            for seller in best_sellers:
                valuation = G[seller][buyer].get('valuation', 0)
                payoff = G[seller][buyer].get('payoff', 0)
                pref_G.add_edge(seller, buyer, valuation=valuation, payoff=payoff)

        return pref_G, preferred_sellers

    def find_constricted_set(preferred_sellers):
        from itertools import combinations

        buyers = list(preferred_sellers.keys())

        
        for r in range(2, len(buyers) + 1):
            for subset in combinations(buyers, r):
                seller_set = set()
                for b in subset:
                    seller_set.update(preferred_sellers[b])

                if len(seller_set) < len(subset):
                    return list(subset), list(seller_set)
              
        return [], []


    def update_prices(prices, constricted, increment=1):
        for s in constricted[1]:
            prices[s] += increment
        return prices

    sellers = [n for n in G.nodes if G.nodes[n].get('bipartite') == 0]
    buyers = [n for n in G.nodes if G.nodes[n].get('bipartite') == 1]
    prices = {s: G.nodes[s].get('price', 0) for s in sellers}

    rounds = []
    round_num = 0
    perfect_matching = False

    while not perfect_matching:  
        pref_G, preferred_sellers = compute_preference_graph(G, prices)
        matching = nx.bipartite.maximum_matching(pref_G, top_nodes=preferred_sellers)
        constricted = find_constricted_set(preferred_sellers)        

        rounds.append((copy.deepcopy(pref_G), copy.deepcopy(prices),
                       copy.deepcopy(matching), copy.deepcopy(preferred_sellers), constricted))
        prices = update_prices(prices, constricted)
        round_num += 1

        if constricted == ([], []): 
            perfect_matching = True
            print("Perfect Matching Found!")
            break

    # Rounds
    fig, axes = plt.subplots(1, len(rounds), figsize=(6 * len(rounds), 6))
    if len(rounds) == 1:
        axes = [axes]

    for i, (pref_G, round_prices, matching, preferred_sellers, constricted) in enumerate(rounds):
        pos = nx.bipartite_layout(pref_G, sellers)

        edge_labels = {(u, v): f"{d['valuation']}→{d['payoff']}"
                       for u, v, d in pref_G.edges(data=True)}

        node_labels = {
            n: f"{n}\nP:{round_prices.get(n, '')}" if n in sellers else str(n)
            for n in pref_G.nodes
        }

        # Draw the graph
        nx.draw(pref_G, pos, ax=axes[i], with_labels=True, labels=node_labels,
                node_color=['lightcoral' if n in sellers else 'skyblue' for n in pref_G.nodes],
                node_size=2000, font_size=9, edge_color='gray')

        for (u, v), label in edge_labels.items():
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            axes[i].text(mx, my, label, fontsize=8, color='black', ha='center')

        axes[i].set_title(f"Round {i+1}")
        axes[i].axis('off')

        # Print details
        print(f"\n === Round {i+1} ===")
        print("Current Prices:")
        for s in sellers:
            print(f"  Seller {s}: Price = {round_prices[s]}")

        print("Preferred Sellers (per buyer):")
        for b in buyers:
            preferred = preferred_sellers.get(b, [])
            print(f"  Buyer {b}: {preferred}  val: {[G[s][b]['valuation'] for s in preferred]}")

        
        if  constricted[0] == []:
            print("\nWe have found a Perfect Matching!")
        else:
            print("Constricted Set:")
            print(" ", constricted)
            print("Updated Prices After Matching:")
            updated_prices = {s: round_prices[s] for s in sellers}
            matched_sellers = set(u for u, v in matching.items() if u in sellers)
            for s in updated_prices:
                if s in find_constricted_set(preferred_sellers)[1]:
                    updated_prices[s] += 1
                print(f"  Seller {s}: {updated_prices[s]}")

    plt.tight_layout()
    plt.show()

def plot_graph(G):
    from networkx.algorithms import bipartite

    sellers = [n for n in G.nodes if G.nodes[n].get('bipartite') == 0]

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

    plt.figure(figsize=(10, 6))
    ax = plt.gca()
    nx.draw(G, pos, with_labels=True, labels=node_labels,
            node_color=node_colors, edge_color='gray', node_size=2000, font_size=10)

    for i, (u, v) in enumerate(G.edges()):
        valuation = G[u][v].get('valuation', '')
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2

        offset = 0.02 * ((-1) ** i) * (i // 2 + 1)
        label_x = mx + offset
        label_y = my

        angle = math.degrees(math.atan2(y1 - y0, x1 - x0))
        if angle > 90 or angle < -90:
            angle += 180  # Keep label upright

        ax.text(label_x, label_y, str(valuation),
                fontsize=9, color='black', ha='center', va='center',
                rotation=angle, rotation_mode='anchor')

    plt.title("Bipartite Market Graph with Valuations and Prices")
    plt.axis('off')
    plt.tight_layout()
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
        interactive_mode(G)


if __name__ == '__main__': 
    main()
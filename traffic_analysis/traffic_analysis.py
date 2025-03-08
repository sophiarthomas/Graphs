import argparse
import os
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize


"""
Potential Energy tool used to find the Nash Equilibrium and Social Optimality of a given graph.

Social Optimality:  

Nash Equilibrium: (S, T) is a Nash equilibrium if S is a best response to T, and T is a best response to S 

Travel Equilibrium: 
"""


def plot_graph(G):
    pos = nx.spring_layout(G)
    labels = {edge: f"{G[edge[0]][edge[1]].get('a', 1)}x + {G[edge[0]][edge[1]].get('b', 0)}" for edge in G.edges}

    plt.figure(figsize=(8,6))
    nx.draw(
        G, 
        pos, 
        with_labels=True, 
        node_color='lightblue', 
        edge_color='red', 
        node_size=2000, 
        font_size=12
        )
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.title("Directed Traffic Network")
    plt.show()

def calculate_travel_cost(flow, a, b): 
    return a * flow + b

def find_paths(G, start, end):
    """Find all simple paths from start to end."""
    # Check if the start and end nodes exist in the graph
    if start not in G.nodes:
        raise ValueError(f"Start node {start} not found in the graph.")
    if end not in G.nodes:
        raise ValueError(f"End node {end} not found in the graph.")
    
    return list(nx.all_simple_paths(G, source=start, target=end))


def compute_path_cost(G, path, flow_distribution): 
    """Computes the total cost of the given path based on the current flow distribution"""
    cost = 0
    for i in range(len(path) - 1): 
        u, v = path[i], path[i+1]
        a, b = G[u][v]['a'], G[u][v]['b']
        flow = flow_distribution.get((u, v), 0)
        cost += calculate_travel_cost(a, flow, b)
    return cost 

def compute_nash_equilibrium(G, n, initial, final):
    """Compute the Nash equilibrium flow distribution"""
    paths = find_paths(G, initial, final)
    flow_distribution = {(u, v): 0 for u, v in G.edges}

    if not paths: 
        raise ValueError("No available paths between start and end nodes.")
    
    path_flows = np.full(len(paths), n / len(paths))

    for _ in range(100): # Max 100 iterations
        costs = [compute_path_cost(G, path, flow_distribution) for path in paths]
        min_cost = min(costs)

        # Reallocate vehicles to the lowers-cost path
        for i, path in enumerate(paths): 
            if costs[i] > min_cost: 
                path_flows[i] -= 1
                path_flows[costs.index(min_cost)] += 1
        
        # Update edge flows
        flow_distribution = {(u, v): 0 for u, v in G.edges}
        for i, path in enumerate(paths): 
            for j in range(len(path) - 1): 
                flow_distribution[(path[j], path[j+1])] += path_flows[i]

        # Stop if all active paths have the same cost
        if len(set(costs)) == 1: 
            break 
    return flow_distribution

def compute_social_optimal(G, n, initial, final):
    """Computes social optimality"""
    paths = find_paths(G, initial, final)

    if not paths: 
        raise ValueError("No availabe paths between start and end nodes. ")
    
    def total_cost(path_flows): 
        """Objective function: minimize total system cost"""
        edge_flows = {edge: 0 for edge in G.edges}

        for i , path in enumerate(paths): 
            for j in range(len(path) - 1): 
                u, v = path[j], path[j+1]
                edge_flows[(u, v)] += path_flows[i]
        return sum(G[u][v]['a'] * flow**2 + G[u][v]['b'] for (u, v), flow in edge_flows.items())

    constraints = [
        {'type': 'eq', 'fun': lambda x: np.sum(x) - n}
    ]

    bounds = [(0, n) for _ in paths]

    result = minimize(total_cost, x0=np.full(len(paths), n / len(paths)), bounds=bounds, constraints=constraints)

    # Convert path flow solution to edge flow
    opt_flow_distribution = {edge: 0 for edge in G.edges}
    for i, path in enumerate(paths):
        for j in range(len(path) - 1):
            u, v = path[j], path[j+1]
            opt_flow_distribution[(u, v)] += result.x[i]

    return opt_flow_distribution


## python ./traffic_analysis.py digraph_file.gml n initial final --plot
def main():
    """Parse command-line arguments and execute graph analysis."""
    parser = argparse.ArgumentParser(description="Traffic Equilibrium and Social Optimality Calculator")
    parser.add_argument("gml_file", type=str, help="Path to the directed graph file in .gml format")
    parser.add_argument("num_vehicles", type=int, help="Number of vehicles in the network")
    parser.add_argument("start_node", type=int, help="Initial node for vehicles")
    parser.add_argument("end_node", type=int, help="Final node for vehicles")
    parser.add_argument("--plot", action="store_true", help="Plot the directed graph")

    args = parser.parse_args()
    
    if not os.path.exists(args.gml_file):
        print(f"Error: File {args.gml_file} not found.")
        return
    
    G = nx.read_gml(args.gml_file)
    G = nx.relabel_nodes(G, lambda x: int(x) if str(x).isdigit() else x)

    n, initial, final = args.num_vehicles, args.start_node, args.end_node

     # Compute Nash equilibrium
    nash_flow = compute_nash_equilibrium(G, n, initial, final)
    print("\nNash Equilibrium Flow Distribution:")
    for edge, flow in nash_flow.items():
        print(f"Edge {edge}: {flow:.2f} vehicles")
    
    # Compute Social Optimality
    opt_flow = compute_social_optimal(G, n, initial, final)
    print("\nSocial Optimal Flow Distribution:")
    for edge, flow in opt_flow.items():
        print(f"Edge {edge}: {flow:.2f} vehicles")
    if args.plot:
        plot_graph(G)

   
if __name__ == "__main__":
    main()



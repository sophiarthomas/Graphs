import argparse
import os
import networkx as nx
import matplotlib.pyplot as plt

"""
Potential Energy tool used to find the Nash Equilibrium and Social Optimality of a given graph.
"""


def plot_graph(G, plot_type):
    return "plotting graph"

def calculate_vehicles(G, n, initial, final):
    return "caluclating vehicles"

## utility functions

def edge_weight(edge): 
    """
    Calculate the weight of an edge based on its attributes.
    Args:
        edge (array): [source, target, a, b]
    """
    x = 1   # x? 
    weight = int = (edge.a * x) + edge.b
    return weight


def travel_equilibrium(G, n, initial, final):
    return "travel equilibrium is ..."

def social_optimality(G, n, initial, final):
    return "social optimality is ..."



## python ./traffic_analysis.py digraph_file.gml n initial final --plot
def main():
    """Parse command-line arguments and execute graph analysis."""
    parser = argparse.ArgumentParser(description="Graph Analysis")
    parser.add_argument("filename", nargs=3, type=str, help="GML file to read graph data.")
    parser.add_argument("--plot", type=str, help="Plot the graph highlighting [C|N|P]")

    args = parser.parse_args()
    
    if not os.path.exists(args.filename):
        print(f"Error: File {args.filename} not found.")
        return
    
    G = nx.read_gml(args.filename)
    n, initial, final = args.filename[1], args.filename[2], args.filename[3]

    # Perform graph analysis based on the provided arguments
    if n and initial and final:
        # Perform some analysis with n, initial, and final
        print(calculate_vehicles(G, n, initial, final))


    if args.plot:
        print(plot_graph(G, args.plot))

   
if __name__ == "__main__":
    main()



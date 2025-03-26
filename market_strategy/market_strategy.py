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

def plot(G):
    pass

def interactive(G): 
    pass 

def main(): 
    """Parse command-line arguments and execute graph analysis."""
    parser = argparse.ArgumentParser(description="Traffic Equilibrium and Social Optimality Calculator")
    parser.add_argument("gml_file", type=str, help="Path to the directed graph file in .gml format")
    parser.add_argument("--plot", action="store_true", help="Plot the directed graph")
    parser.add_argument("--interactive", action="store_true", help="Show the output of every round graph (Preference seller graph)")


    args = parser.parse_args()
    
    if not os.path.exists(args.gml_file):
        print(f"Error: File {args.gml_file} not found.")
        return
    
    G = nx.read_gml(args.gml_file)


if __name__ == '__main__': 
    main()
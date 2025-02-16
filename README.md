# Graphs Assignment 
## Overview 
Python program that accepts gml files as input or generates random graphs using the NetworkX library
- Read graphs from .gml files
- Generate new random graphs with labeled nodes
- Compute the shortest paths from a specified node using BFS
- Visualize the graph 
- Save the generated graph to a .gml file

## Networkx Libarary
- nx.read_gml
- nx.write_gml
- nx.bfs_tree
- nx.erdos_renyi_graph
- nx.relabel_nodes
- nx.draw
- nx.kamada_kawai_layout
- nx.draw_networkx_edges
- nx.drawnetworkx_nodes


## Requirements 
```
pip install networkx matplotlib
```

## Usage 
Run the script using this command format: 
`python graph.py [options]`

### Options: 
#### 1. Input an Existing Graph
`python graph.py --input graph_file.gml`

#### 2. Create a Random Graph 
`python graph.py --create_random_graph n c --output out_graph_file.gml`
-  n: Number of nodes.
- c: Constant affecting edge probability (p = (c ln n) / n).
- Saves the graph to out_graph_file.gml.

#### 3. Compute Shortest Paths (BFS) from a Node
`python graph.py --input graph_file.gml --BFS 1`

#### 4. Plot the Graph 
`python graph.py --input graph_file.gml --plot`

## Example Command 
```
python graph.py --create_random_graph 100 1.1 --BFS 1 --plot --output my_graph.gml
```

This creates a 100-node random graph, computes BFS from A, plots the graph, and saves it as my_graph.gml.

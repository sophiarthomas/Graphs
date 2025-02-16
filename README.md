# Graph Analysis Tool

This Python program analyzes graphs from `gml` files, computing cluster coefficients, neighborhood voerlaps, and partitioning graphs into components. Also providing options for interactive plotting and verification of homophily and graph balance.

# Installation

Ensure you have Python 3 installed. Required libraries:

```
pip install networkx numpy matplotlib scipy
```

# Usage

The script runs from the terminal with the following syntax:

```
python graph_analysis.py graph_file.gml --components n --plot [C|N|P] --verify_homophily --verify_balanced_graph --output out_graph_file.gml
```

## Arguments:

graph_file.gml: Input file containing the graph

`--components n`: Partition graph into n components

`--plot [C|N|P]`: Choose graph visualization method:

`C`: Clustering coefficient

`N`: Neighborhood overlap (interactive)

`P`: Node attributes

`--verify_homophily`: Test for homophily in the graph

`--verify_balanced_graph`: Check if the graph is balanced

`--output out_graph_file.gml`: Save modified graph to a new file

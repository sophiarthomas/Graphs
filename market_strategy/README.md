# Market Strategy Analysis

This Python program analyzes a bipartite market graph where buyers are connected to sellers via edges with valuations. Sellers have prices, and buyers choose preferred sellers based on payoff (valuation - price). The script performs visual and interactive rounds to simulate market clearing using constricted set detection and dynamic price updates.

## Files

- `market_strategy.py` – Main Python script
- `market.gml` – Input GML file defining the market graph (nodes and edges)

## Requirements

- Python 3.6+
- Dependencies:
  - `networkx`
  - `matplotlib`

Install dependencies with:

```bash
pip install networkx matplotlib numpy
```

## Graph Format
The graph must be in Graph Modelling Language (.gml) and structured as a bipartite graph:

- Nodes in set A (sellers): IDs 0 to n-1, must include a price attribute

- Nodes in set B (buyers): IDs n to 2n-1

- Edges: must include a valuation attribute indicating how much a buyer values the seller

Each node must have a bipartite attribute:

- bipartite = 0 for sellers

- bipartite = 1 for buyers

## How to Run 
```bash
python ./market_strategy.py market.gml [--plot] [--interactive]
```

## Arguments 
- market.gml: Path to the GML file

- --plot: Displays a visual representation of the bipartite graph with seller prices and edge valuations

- --interactive: Runs the full market clearing simulation step-by-step, with visualizations and printed updates


## Output 
Each round displays 
- A visual preference graph 
- Details such as prices, valuations, preferred sellers, constricted sets (when not a perfect matching)

When a perfect matching is achieved, the market is considered cleared and the program is complete.





# Dynamic Population Simulation

This Python program simulates either a **cascade effect** or the spread of **COVID-19** using the **SIR model** across a network. The graph must be provided in `.gml` format.

## Features

- Cascade Simulation based on threshold activation
- COVID-19 SIR Simulation with:
  - Infection probability
  - Death probability
  - Vaccination and shelter-in-place proportions
- Dynamic graph visualization at each step using `--interactive`
- Infection curve plotting over time using `--plot`
- Custom color-coded node states depending on simulation type

## Requirements

- Python 3.x
- Packages:
  - networkx
  - matplotlib

To install dependencies, run:

```
pip install networkx matplotlib
```

## Running the project

```
python dynamic_population.py graph.gml --action [cascade|covid] --initiator <node_ids> [options]
```

### Required Arguments

`graph.gml`: Path to your graph file (must be in .gml format)

`--action`: Choose either cascade or covid

`--initiator`: Comma-separated list of node IDs to start the simulation

### Optional Arguments (for COVID mode):

`--threshold` or `-t`: Threshold to activate nodes in cascade (default is 0.5)

`--probability_of_infection` or `-pi`: Chance an infected node spreads the virus (default is 0.05)

`--probability_of_death` or `-pd`: Chance an infected node dies each step (default is 0.01)

`--lifespan` or `-l`: Number of simulation steps (default is 50)

`--shelter` or `-s`: Proportion of nodes that are sheltered and cannot be infected (value between 0 and 1)

`--vaccination` or `-pv`: Proportion of nodes vaccinated at the start (value between 0 and 1)

`--interactive` or `-i`: If included, animates the graph after each step

`--plot` or `-p`: If included, plots the number of new infections per day

## Examples

### Example 1: Cascade Simulation

```
python dynamic_population.py graph.gml --action cascade --initiator 1,2,3 --threshold 0.4 --interactive
```

This runs a cascade simulation starting at nodes 1, 2, and 3 with a 0.4 threshold and visualizes each round.

### Example 2: COVID Simulation

```
python dynamic_population.py graph.gml --action covid --initiator 0,4 --probability_of_infection 0.03 --probability_of_death 0.01 --lifespan 60 --shelter 0.2 --vaccination 0.3 --interactive --plot
```

This simulates the spread of COVID-19 starting from nodes 0 and 4 with infection and death rates, 20% of the population sheltered, 30% vaccinated, and visualizes + plots the simulation.

## Note

- Your input graph must be in .gml format and use node labels that match your --initiator values.

- Sheltered and vaccinated nodes will not participate in infection spread.

- Visualizations and plots help track the spread step by step and overall.

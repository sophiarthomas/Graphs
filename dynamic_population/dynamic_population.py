import argparse
import os
import sys
import random
import networkx as nx
import matplotlib.pyplot as plt

"""
Upddate: 
- simulate_cascade works
- simulate_covid needs to be redone completely
- plot covid redone
"""

# Node status
SUSCEPTIBLE = "S"
INFECTED = "I"
RECOVERED = "R"
DEAD = "D"

def parse_args():
    parser = argparse.ArgumentParser(description="Simulate cascade or COVID-19 spread on a graph.")
    parser.add_argument("graph_file", help="Path to the graph GML file")
    parser.add_argument("--action", choices=["cascade", "covid"], required=True)
    parser.add_argument("--initiator", required=True, help="Comma-separated node IDs")
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--probability_of_infection", type=float, default=0.05)
    parser.add_argument("--probability_of_death", type=float, default=0.01)
    parser.add_argument("--lifespan", type=int, default=50)
    parser.add_argument("--shelter", type=float, default=0.0)
    parser.add_argument("--vaccination", type=float, default=0.0)
    parser.add_argument("--interactive", action="store_true")
    parser.add_argument("--plot", action="store_true")
    return parser.parse_args()

def load_graph(path):
    if not os.path.exists(path): 
        raise FileNotFoundError(f"Graph file {path} does not exist.")
    return nx.read_gml(path)

def simulate_cascade(G, initiators, threshold, interactive):
    """
    @param G: The graph to simulate 
    @param initiators: The initial nodes to start the cascade
    @param threshold: The threshold for a node to become active
    @param interactive: If True, show the graph at each step
    """
    active = set(initiators)
    for n in G.nodes: 
        G.nodes[n]['state'] = 'inactive'
    for n in active: 
        G.nodes[n]['state'] = 'active'
    
    changed = True
    round = 0
    prev_active = set(active)
    while changed: 
        changed = False
        for n in G.nodes: 
            if G.nodes[n]['state'] == 'inactive': 
                neighbors = list(G.neighbors(n))
                active_neighbors = sum(G.nodes[n]['state'] == 'active' for n in neighbors)
                if neighbors and active_neighbors / len(neighbors) >= threshold: 
                    G.nodes[n]['state'] = 'active'
                    active.add(n)   
                    changed = True
        if interactive and (len(active) != len(prev_active)): # Show the graph at each Round
            prev_active = active.copy()
            round += 1
            draw_graph(G, node_color_by_state(G), title=f"Round {round}")
    draw_graph(G, node_color_by_state(G), title=f"Round {round} - Final State")
        

def simulate_covid(G, initiators, p_infect, p_death, lifespan, shelter, vaccination, interactive, plot):
    pass
                
def draw_graph(G, color_map, title):
    pos = nx.spring_layout(G, seed=42)
    plt.figure()
    plt.title(title)
    nx.draw(G, pos=pos, with_labels=True, node_color=color_map, node_size=500)
    plt.show()

def node_color_by_state(G):
    colors = {
        'inactive': 'green', 
        'active': 'red', 
        SUSCEPTIBLE: 'yellow',
        INFECTED: 'red',
        RECOVERED: 'green',
        DEAD: 'black'
    }
    return [colors[G.nodes[n]['state']] for n in G.nodes]

def plot_infection_curve(infections):
    plt.figure()
    plt.plot(range(len(infections)), infections, marker='o')
    plt.title("Daily New Infections")
    plt.xlabel("Days")
    plt.ylabel("New Infections")
    plt.grid(True)
    plt.show()
        

def main():
    args = parse_args()
    try: 
        G = load_graph(args.graph_file)
    except Exception as e: 
        print(e)
        return 
    
    initiators = args.initiator.split(",")

    if args.action == "cascade": 
        simulate_cascade(G, initiators, args.threshold, args.interactive)
    elif args.action == "covid": 
        infections = simulate_covid(G, initiators, args.probability_of_infection, 
                                    args.probability_of_death, 
                                    args.lifespan, 
                                    args.shelter, args.vaccination, args.interactive
                                    , args.plot)
        if args.plot: 
            plot_infection_curve(infections)

def test_main():
    args = parse_args()
    G = load_graph(args.graph_file)
    draw_graph(G, node_color_by_state(G), title="Initial Graph")

if __name__ == "__main__": 
    main() 
    # test_main()

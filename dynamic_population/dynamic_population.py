import argparse
import os
import random
import networkx as nx
import matplotlib.pyplot as plt
import time

# Node status
SUSCEPTIBLE = "S"
INFECTED = "I"
RECOVERED = "R"
DEAD = "D"
SHELTER = "SH"

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
    draw_graph(G, node_color_by_state(G), title=f"Round {round} - Initial State")
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
        

def simulate_covid(G, initiators, p_infect, p_death, lifespan, shelter=0, vaccination=0, interactive=False, plot=False):
    new_infections_per_step = []

    # Initialize all nodes to susceptible
    for node in G.nodes:
        G.nodes[node]['state'] = SUSCEPTIBLE

    # Set initiators to infected
    for node in initiators:
        G.nodes[node]['state'] = INFECTED
    
    draw_graph(G, node_color_by_state(G), title="Initial State")

    for  step in range(1, lifespan+1):
        new_infections = 0
        next_states = {}

        # Determine state updates
        for node in G.nodes:
            state = G.nodes[node]['state'] # state of the current node
            if state == INFECTED: # only checking infected nodes and thier neighbors 
                for neighbor in G.neighbors(node):
                    if G.nodes[neighbor]['state'] == SUSCEPTIBLE or G.nodes[neighbor]['state'] == RECOVERED:
                        if random.random() < p_infect:
                            next_states[neighbor] = INFECTED
                            new_infections += 1
                # Recovery (ignoring death for now; you can add that logic later)
                next_states[node] = RECOVERED

        # Apply state updates
        for node, new_state in next_states.items():
            if new_state != RECOVERED: 
                G.nodes[node]['state'] = new_state
            

        new_infections_per_step.append(new_infections)

        # if interactive:
        #         draw_graph(G, node_color_by_state(G), title=f"Step {step}")

        # Apply recovery state updates 
        for node, new_state in next_states.items():
            if new_state == RECOVERED: 
                G.nodes[node]['state'] = new_state
        

        

    if plot:
        plot_infection_curve(new_infections_per_step, lifespan)
    if interactive:
        draw_graph(G, node_color_by_state(G), title=f"Step {step}")


                
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
        DEAD: 'black',
        SHELTER: 'blue'
    }
    return [colors[G.nodes[n]['state']] for n in G.nodes]

def plot_infection_curve(infections, lifespan):
    plt.figure(figsize=(10, 6))
    plt.plot(range(lifespan), infections, marker='o')
    plt.xlabel('Day')
    plt.ylabel('New Infections')
    plt.title('Covid-19 Spread Over Time (SIR Model)')
    plt.grid()
    plt.tight_layout()
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

def test_main():
    args = parse_args()
    G = load_graph(args.graph_file)
    draw_graph(G, node_color_by_state(G), title="Initial Graph")

if __name__ == "__main__": 
    main() 
    # test_main()

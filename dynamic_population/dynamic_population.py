import argparse
import os
import random
import networkx as nx
import matplotlib.pyplot as plt
import time


# Node status
SUSCEPTIBLE = "SUSCEPTIBLE"
INFECTED = "INFECTED"
RECOVERED = "RECOVERED"
DEAD = "DEAD"
SHEL_VAC = "SHELTER/VACCINATED"

colors = {
    'cascade': {
        'inactive': '#93d286',
        'active': '#ca2f2f',
    },
    'covid': { 
        SUSCEPTIBLE: '#f7dc6f', #yellow
        INFECTED: '#ca2f2f', #red
        RECOVERED: '#93d286', #green
        DEAD: '#71173d', #dark red
        SHEL_VAC: '#ccd1d1' #gray
        }
    }

def parse_args():
    parser = argparse.ArgumentParser(description="Simulate cascade or COVID-19 spread on a graph.")
    parser.add_argument("graph_file", help="Path to the graph GML file")
    parser.add_argument("-a","--action", choices=["cascade", "covid"], required=True)
    parser.add_argument("-init", "--initiator", required=True, help="Comma-separated node IDs")
    parser.add_argument("-t", "--threshold", type=float, default=0.5)
    parser.add_argument("-pi","--probability_of_infection", type=float, default=0.05)
    parser.add_argument("-pd", "--probability_of_death", type=float, default=0.01)
    parser.add_argument("-l", "--lifespan", type=int, default=50)
    parser.add_argument("-s", "--shelter", type=float, default=0.0)
    parser.add_argument("-pv", "--vaccination", type=float, default=0.0)
    parser.add_argument("-i", "--interactive", action="store_true")
    parser.add_argument("-p", "--plot", action="store_true")
    return parser.parse_args()

def load_graph(path):
    if not os.path.exists(path): 
        raise FileNotFoundError(f"Graph file {path} does not exist.")
    return nx.read_gml(path)

def simulate_cascade(G, initiators, threshold, interactive, action):
    """
    @param G: The graph to simulate 
    @param initiators: The initial nodes to start the cascade
    @param threshold: The threshold for a node to become active
    @param interactive: If True, show the graph at each step
    @param action: The action to perform (cascade or covid)
    """
    active = set(initiators)
    for n in G.nodes: 
        G.nodes[n]['state'] = 'inactive'
    for n in active: 
        G.nodes[n]['state'] = 'active'
    
    round = 0
    # prev_active = set(active)
    if interactive:
        draw_graph(G, action, node_color_by_state(G, action), title=f"Round {round} - Initial State")

    while True: 
        newley_activated = set()

        for n in G.nodes: 
            if G.nodes[n]['state'] == 'inactive': 
                neighbors = list(G.neighbors(n))
                if not neighbors: 
                    continue
                active_neighbors = sum(G.nodes[neighbor]['state'] == 'active' for neighbor in neighbors)
                if active_neighbors / len(neighbors) >= threshold: 
                    newley_activated.add(n)
        if not newley_activated:
            break

        for n in newley_activated: 
            G.nodes[n]['state'] = 'active'
            active.add(n)

        round += 1


        if interactive: # Show the graph at each Round
            draw_graph(G, action, node_color_by_state(G, action), title=f"Round {round}")
    if not interactive:       
        draw_graph(G, action, node_color_by_state(G, action), title=f"Round {round} - Final State")
        

def simulate_covid(G, initiators, p_infect, p_death, lifespan, action, shelter=0, vaccination=0, interactive=False, plot=False):
    new_infections_per_step = []

    # Initialize all nodes to susceptible
    for node in G.nodes:
        G.nodes[node]['state'] = SUSCEPTIBLE

    # Set initiators to infected
    for node in initiators:
        G.nodes[node]['state'] = INFECTED

    # Apply vaccination and shelter
    apply_shelter_and_vaccination(G, shelter, vaccination, initiators)
    
    if interactive: 
        draw_graph(G, action, node_color_by_state(G, action), title="Initial State")

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
                # Death or Recovery
                if random.random() < p_death: 
                    next_states[node] = DEAD
                else: 
                    next_states[node] = RECOVERED

        # Apply state updates
        for node, new_state in next_states.items():
            if new_state != RECOVERED: 
                G.nodes[node]['state'] = new_state
            

        new_infections_per_step.append(new_infections)

        # if interactive:
        #         draw_graph(G, action, node_color_by_state(G, action), title=f"Step {step}")

        # Apply recovery state updates 
        for node, new_state in next_states.items():
            if new_state == RECOVERED: 
                G.nodes[node]['state'] = new_state
    
    if plot:
        plot_infection_curve(new_infections_per_step, lifespan)
    if interactive:
        draw_graph(G, action, node_color_by_state(G, action), title=f"Step {step}")

def apply_shelter_and_vaccination(G, shelter, vaccination, initiators): 
    nodes = list(G.nodes)
    # Apply shelter
    shelter_count = int(len(nodes) * shelter)
    shelter_nodes = random.sample([n for n in nodes if n not in initiators and G.nodes[n]['state'] != RECOVERED], shelter_count)
    for node in shelter_nodes: 
        G.nodes[node]['state'] = SHEL_VAC

    # Vaccination (nodes become recovered)
    vax_count = int(len(nodes) * vaccination)
    vax_nodes = random.sample([n for n in nodes if n not in initiators], vax_count)
    for node in vax_nodes:
        G.nodes[node]['state'] = SHEL_VAC

def draw_graph(G, action, color_map, title):
    pos = nx.spring_layout(G, seed=42)
    plt.figure()
    plt.title(title)
    nx.draw(G, pos=pos, with_labels=True, node_color=color_map, node_size=500)
    plot_lengend(action)
    plt.show()

def node_color_by_state(G, action):
    state_colors = colors[action]
    return [state_colors.get(G.nodes[n]['state']) for n in G.nodes]

def plot_lengend(action): 
    if action == "cascade":
        state_colors = colors['cascade']
    else:
        state_colors = colors['covid']

    for state, color in state_colors.items():
        plt.scatter([], [], color=color, label=state)
    plt.legend()
    plt.show()

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
        simulate_cascade(G, initiators, args.threshold, args.interactive, args.action)
    elif args.action == "covid": 
        infections = simulate_covid(G, initiators, args.probability_of_infection, 
                                    args.probability_of_death, 
                                    args.lifespan, args.action,
                                    args.shelter, args.vaccination, args.interactive
                                    , args.plot)

def test_main():
    args = parse_args()
    G = load_graph(args.graph_file)
    action = 'covid'
    # state
    for n in G.nodes: 
        G.nodes[n]['state'] = 'inactive'
    draw_graph(G, action, node_color_by_state(G, action), title="Initial Graph")

if __name__ == "__main__": 
    main() 
    # test_main()

import numpy as np
import networkx as nx
from wire_util import draw_current, parse_file, create_graf_from_solution, validate_solution

#creating matring for nodal analisis with the following assumptions:
# 1. There are no wires with 0 resistance in the network
# 2. The only component with 0 resitance is the voltage source
# 3. The tap point is the ground reference for the network
def create_nodal_analisis_matrix(graph: nx.Graph, source: int, tap: int) -> np.ndarray:
    N = graph.number_of_nodes()
    matrix = np.zeros((N,N), dtype=np.float64)
    for u, v, data in graph.edges(data=True):
        # Adding conductances to the diagonal and subtracting from the rest of the matrix
        # If there is no edge between nodes the value in the matrix will be 0
        matrix[u, v] -= 1/data['resistance']
        matrix[v, u] -= 1/data['resistance']
        matrix[u, u] += 1/data['resistance']
        matrix[v, v] += 1/data['resistance']
    # Here we account for the 0 internal resistance pure voltage source
    # by using modifed nodal analisis
    matrix = np.pad(matrix, ((0, 1), (0, 1)),'constant', constant_values=(0))
    matrix[-1, source] = 1
    matrix[-1, tap] = -1
    matrix[source, -1] = 1
    matrix[tap, -1] = -1
    return matrix

def solve_nodal_analisis(graph: nx.Graph, source: int, tap: int, voltage: int):
    N = graph.number_of_nodes()
    matrix = create_nodal_analisis_matrix(graph, source, tap)
    # Currents in every equation must equal 0
    right = np.zeros(N+1)
    # This is setting the pure voltage source are part of modifed nodal analisis
    right[-1] = voltage
    solution = solution = np.linalg.solve(matrix, right)
    #Returns the voltages in each node and the current through the voltage source
    return [solution[i] - solution[0] for i in range(N)], -solution[-1]

def vertex_to_edge_cycle(cycle):
    new = []
    for v in range(len(cycle)-1):
        new.append((cycle[v], cycle[v+1]))
    new.append((cycle[-1], cycle[0]))
    return new

# failed apptempt to write a slver that uses kirchoffs
def solve_kirhoffs(graph: nx.Graph, source: int, tap: int, voltage: int):
    new = nx.DiGraph()
    i = 0
    g_dict = {}
    for u, v, d in graph.edges(data=True):
        u, v = min(u, v), max(u, v)
        new.add_edge(u, v, resistance = d['resistance'])
        g_dict[(u, v)] = i
        i += 1  
    new.add_edge(min(tap, source), max(tap, source))
    graph.add_edge(tap, source)


    matrix = np.zeros((new.number_of_edges(), new.number_of_edges()))
    right = np.zeros(new.number_of_edges())
    
    
    for i in range(new.number_of_nodes()-1):
        for u, v in new.edges(i):
            u, v = min(u, v), max(u, v)
            id = g_dict[(u, v)]
            if i == u:
                matrix[i, id] = 1
            else:
                matrix[i, id] = -1
    
    cycles = [c for c in nx.simple_cycles]

    start = new.number_of_nodes()-1

    for i in range(new.number_of_nodes()-1, new.number_of_edges()):
        egde_cycle = vertex_to_edge_cycle(cycles[i-start])
        if (source, tap) in egde_cycle:
            egde_cycle.remove((source, tap))
            right[i] = -voltage
        elif (tap, source) in egde_cycle:
            egde_cycle.remove((tap, source))
            right[i] = -voltage
        for egde in egde_cycle:
            id = g_dict[egde]
            matrix[i, id] = new.get_edge_data(egde[0], egde[1])['resistance']

    currents = np.linalg.solve(matrix, right)
    print(currents)
    return 0

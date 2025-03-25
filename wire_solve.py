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

def example():
    graph = parse_file("test.txt")
    sol, i = solve_nodal_analisis(graph, 1, 0, 10)
    descp = {"source":1, "tap":0, "voltage":10, "current":i}
    p = create_graf_from_solution(graph, sol)
    validate_solution(p.copy(), descp, True)
    draw_current(p, descp)

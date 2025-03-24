import numpy as np
import networkx as nx
from wire_vis import draw_current

def parse_file(filename: str) -> nx.Graph:
    file = open(filename)
    graph = nx.read_edgelist(file, nodetype=int, data=(('resistance', float),))
    file.close()
    return graph

def create_nodal_analisis_matrix(graph: nx.Graph, source: int, tap: int) -> np.ndarray:
    N = graph.number_of_nodes()
    matrix = np.zeros((N,N), dtype=np.float64)
    for u, v, data in graph.edges(data=True):
        matrix[u, v] -= 1/data['resistance']
        matrix[v, u] -= 1/data['resistance']
        matrix[u, u] += 1/data['resistance']
        matrix[v, v] += 1/data['resistance']
    matrix = np.pad(matrix, ((0, 1), (0, 1)),'constant', constant_values=(0))
    matrix[N, source] = 1
    matrix[N, tap] = -1
    matrix[source, N] = 1
    matrix[tap, N] = -1
    return matrix

def solve_nodal_analisis(graph: nx.Graph, source: int, tap: int, voltage: int) -> np.ndarray:
    N = graph.number_of_nodes()
    matrix = create_nodal_analisis_matrix(graph, source, tap)
    right = np.zeros(N+1)
    right[-1] = voltage
    solution = solution = np.linalg.solve(matrix, right)
    return [solution[i] - solution[0] for i in range(N)]


def create_graf_from_solution(input_graf: nx.Graph, potentials) -> nx.DiGraph:
    g = nx.DiGraph()
    for u, v, data in input_graf.edges(data=True):
        if potentials[u] > potentials[v]:
            g.add_edge(u, v, current = (potentials[u] - potentials[v])/data["resistance"])
        elif potentials[v] > potentials[u]:
            g.add_edge(v, u, current = (potentials[v] - potentials[u])/data["resistance"])
        else:
            g.add_edge(u, v, current = 0)
            g.add_edge(v, u, current = 0)
    return g

graph = parse_file("test.txt")
sol = solve_nodal_analisis(graph, 1, 0, 10)
draw_current(create_graf_from_solution(graph, sol))

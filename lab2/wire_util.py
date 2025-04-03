import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl

# This function draws the resistance network with a color map as the visual current indicator
# every edge has to have "current" and "resistance" propety
# data is a dictionary with 4 atributes = (source, tap, voltage, current)
# pos is a networkx layout
def draw_current(graph: nx.DiGraph, data: dict, pos = None, lables = True, nodesize=100, edge_width=2):
    if pos is None:
        pos = nx.nx_pydot.graphviz_layout(graph)
    edge_colors = [d[2] for d in graph.edges.data('current')]
    cmap = plt.cm.plasma

    nodes = nx.draw_networkx_nodes(graph, pos, node_size=nodesize)
    edges = nx.draw_networkx_edges(
        graph, pos,
        arrowstyle="->", arrowsize=5*edge_width, width=edge_width, edge_cmap=cmap,
        edge_color=edge_colors
    )
    if lables: edge_labels = {(x,y):"I=%.2fA\nR=%.1fΩ"%(d['current'], d['resistance']) for x,y,d in graph.edges(data=True)}
    graph.add_edge(data["tap"], data["source"])
    battery_edge = nx.draw_networkx_edges(graph, pos, [(data["tap"], data["source"])],
        arrowstyle="->", arrowsize=5*edge_width, width=edge_width, edge_color="r"
    )
    if lables:
        edge_labels[(data["tap"], data["source"])] = "I=%.2fA\nU=%.2fV"%(data["current"], data["voltage"])
        drawn_lables = nx.draw_networkx_edge_labels(graph, pos, edge_labels, font_size=5)

    pc = mpl.collections.PatchCollection(edges, cmap=cmap)
    pc.set_array(edge_colors)

    ax = plt.gca()
    ax.set_axis_off()
    plt.colorbar(pc, ax=ax)
    plt.show()

# Parses a text file and creates a graph ready for nodal analisis
# The text file must be a list of edges and a resisance value for each edge
def parse_file(filename: str) -> nx.Graph:
    file = open(filename)
    graph = nx.read_edgelist(file, nodetype=int, data=(('resistance', float),))
    file.close()
    return graph

# Creates a graf from the nodal analisis solution thats ready to be displayed
def create_graf_from_solution(input_graf: nx.Graph, potentials) -> nx.DiGraph:
    g = nx.DiGraph()
    for u, v, data in input_graf.edges(data=True):
        if potentials[u] > potentials[v]:
            g.add_edge(u, v, current = (potentials[u] - potentials[v])/data["resistance"], resistance =  data["resistance"])
        elif potentials[v] > potentials[u]:
            g.add_edge(v, u, current = (potentials[v] - potentials[u])/data["resistance"], resistance = data["resistance"])
        elif v == u:
            continue
        else:
            g.add_edge(u, v, current = 0, resistance = data["resistance"])
            g.add_edge(v, u, current = 0, resistance = data["resistance"])
    return g

#checks if the solution is correct according to kirchoffs law
#data is the same dictionary thats used for drawing the solution
def validate_solution(graph: nx.DiGraph, data: dict, verbose:bool = False):
    graph.add_edge(data["tap"], data["source"], current = data["current"])
    for i in graph.nodes():
        in_current = sum([d["current"] for _,_,d in graph.in_edges(i, data=True)])
        out_current = sum([d["current"] for _,_,d in graph.out_edges(i, data=True)])
        if abs(in_current - out_current) > 10 ** -10:
            if verbose: print("Fail")
            return False
    if verbose: print("Succes")
    return True
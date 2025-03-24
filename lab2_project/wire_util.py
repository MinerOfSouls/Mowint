import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl

# every edge has to have "current" propety
def draw_current(graph: nx.Graph):
    pos = nx.spring_layout(graph)
    edge_colors = [d[2] for d in graph.edges.data('current')]
    cmap = plt.cm.plasma

    nodes = nx.draw_networkx_nodes(graph, pos, node_size=200)
    edges = nx.draw_networkx_edges(
        graph, pos,
        arrowstyle="->", arrowsize=10, width=2,
        edge_color=edge_colors, edge_cmap=cmap
    )
    edge_labels = {(x,y):"%.2f"%d['current'] for x,y,d in graph.edges(data=True)}
    
    lables = nx.draw_networkx_edge_labels(graph, pos, edge_labels)

    pc = mpl.collections.PatchCollection(edges, cmap=cmap)
    pc.set_array(edge_colors)

    ax = plt.gca()
    ax.set_axis_off()
    plt.colorbar(pc, ax=ax)
    plt.show()

def parse_file(filename: str) -> nx.Graph:
    file = open(filename)
    graph = nx.read_edgelist(file, nodetype=int, data=(('resistance', float),))
    file.close()
    return graph
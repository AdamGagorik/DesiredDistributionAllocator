"""
Unit test utilities.
"""
import networkx as nx
import logging


def make_graph(nodes: list, edges: list) -> nx.DiGraph:
    """
    Create a graph for testing.

    Parameters:
        nodes: A list of (label, attrs) for each node.
        edges: A list of (node1, node2) for each edge.

    Returns:
        A directed graph instance.
    """
    graph = nx.DiGraph()

    for node, kwargs in nodes:
        graph.add_node(node, **kwargs)

    for e1, e2 in edges:
        graph.add_edge(e1, e2)

    return graph


def show_graph(name: str, graph: nx.DiGraph):
    """
    Debug the graph to the logger.

    Parameters:
        name: A short description for the graph.
        graph: The graph to debug with the logger.
    """
    # noinspection PyBroadException
    try:
        import allocate.network.visualize
        logging.debug('%s\n%s', name, allocate.network.visualize.text(graph, attrs=True))
    except Exception:
        logging.error('can not display graph! %s', name)

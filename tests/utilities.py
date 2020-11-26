"""
Unit test utilities.
"""
import holoviews as hv
import networkx as nx
import panel.viewable
import panel as pn
import logging
import typing


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


def show_graph(name: str, graph: nx.DiGraph, algo_graph: bool = False, **kwargs):
    """
    Debug the graph to the logger.

    Parameters:
        name: A short description for the graph.
        graph: The graph to debug with the logger.
        algo_graph: Assume the kwargs are that of the algo graph?
    """
    # noinspection PyBroadException
    try:
        import allocate.network.visualize
        if algo_graph and not kwargs:
            kwargs = allocate.network.visualize.formats_all
        else:
            kwargs = kwargs if kwargs else dict(attrs=True)
        logging.debug('%s\n%s', name, allocate.network.visualize.text(graph, **kwargs))
    except Exception:
        logging.error('can not display graph! %s', name)


def show_plot(plot: typing.Union[hv.Element, panel.viewable.Viewable], show: bool):
    """
    Serve a holoviews or panel object for debugging.

    Parameters:
        plot: The holoviews or panel object to show.
        show: Open the browser with the plot displayed?
    """
    if show:
        gspec = pn.GridSpec(sizing_mode='stretch_width')
        gspec[0, 0] = plot
        gspec.show()

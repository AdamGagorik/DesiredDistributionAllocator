"""
Methods for creating a graph representation of the problem.
"""
import networkx.exception
import networkx as nx
import pandas as pd
import numpy as np
import logging

import allocate.network.algorithms


def network_has_no_cycles(graph: nx.DiGraph) -> bool:
    """
    The network is a directed acyclic graph?
    """
    try:
        cycle = nx.algorithms.find_cycle(graph, orientation='ignore')
        logging.error('network cycle found!')
        for edge in cycle:
            logging.error('edge: %s -> %s', *edge[:2])
        return False
    except networkx.exception.NetworkXNoCycle:
        return True


def network_has_no_orphan_children(graph: nx.DiGraph) -> bool:
    """
    All children in the network have a parent?
    """
    graph = graph.to_undirected(as_view=True)
    connected = nx.is_connected(graph)
    if not connected:
        logging.error('network is not connected!')
        for subgraph in nx.connected_components(graph):
            logging.error('sub graph: %s', subgraph)
        return False
    else:
        return True


def network_children_only_have_single_parent(graph: nx.DiGraph) -> bool:
    """
    All children in the network have a single parent?
    """
    valid = True
    if len(graph) > 1:
        # noinspection PyTypeChecker
        for n, degree in graph.in_degree:
            if degree > 1:
                logging.error('degree %d > 1 for node: %s', degree, n)
                valid = False

    if not valid:
        logging.error('nodes have multiple predecessors!')

    return valid


def network_sums_to_100_percent_at_each_level(graph: nx.DiGraph, key: str, expected: float = 1.0) -> bool:
    """
    The fraction desired at each level sums to 100 percent?
    """
    source = allocate.network.algorithms.get_graph_root(graph)
    values = nx.get_node_attributes(graph, key)
    depths = networkx.single_source_shortest_path_length(graph, source)
    totals = pd.DataFrame(depths, index=[0]).T.groupby(by=0).apply(lambda group: sum(group.index.map(values)))
    is_100 = np.isclose(totals.values, expected, rtol=1.0e-5, atol=1.0e-8)
    if not np.all(is_100):
        for level, level_is_100 in enumerate(is_100):
            if not level_is_100:
                logging.error('%s does not sum to 100 for level %d', key, level)
        return False
    else:
        return True

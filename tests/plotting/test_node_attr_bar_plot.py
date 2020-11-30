"""
Unit tests for module.
"""
import networkx as nx
import pandas as pd
import logging
import pytest

import allocate.plotting.node_attr_bar_plot
import allocate.network.algorithms
import tests.utilities


@pytest.fixture()
def graph() -> nx.DiGraph:
    frame = pd.DataFrame([
        dict(label='1', current_value=8000.0, optimal_ratio=1.0e2, amount_to_add=100.0, children=('2', '3', '4')),
        dict(label='2', current_value=2500.0, optimal_ratio=4.5e1, amount_to_add=000.0, children=()),
        dict(label='3', current_value=5000.0, optimal_ratio=2.0e1, amount_to_add=000.0, children=()),
        dict(label='4', current_value=500.00, optimal_ratio=3.5e1, amount_to_add=000.0, children=('5', '6')),
        dict(label='5', current_value=200.00, optimal_ratio=2.5e1, amount_to_add=000.0, children=()),
        dict(label='6', current_value=300.00, optimal_ratio=7.5e1, amount_to_add=000.0, children=())
    ])
    logging.debug('frame\n%s', frame)
    graph: nx.DiGraph = allocate.network.algorithms.create(frame)
    tests.utilities.show_graph('graph', graph, algo_graph=True)
    yield graph


def test_get_plot_object(graph: nx.DiGraph, show: bool = False):
    hv_obj = allocate.plotting.node_attr_bar_plot.get_plot_object(graph)
    tests.utilities.show_plot(hv_obj, show)


def test_get_plot_object_leaves_only(graph: nx.DiGraph, show: bool = False):
    hv_obj = allocate.plotting.node_attr_bar_plot.get_plot_object(
        graph, graph, graph, should_extract=allocate.network.algorithms.is_leaf_node)
    tests.utilities.show_plot(hv_obj, show)

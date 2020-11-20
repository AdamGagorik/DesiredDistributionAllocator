"""
Unit tests for module.
"""
import networkx as nx
import pandas as pd
import logging
import pytest

import allocate.network.algorithms
import allocate.network.visualize
import tests.utilities


@pytest.mark.parametrize('graph,expected_root', [
    (nx.DiGraph([(1, 2), (2, 3), (3, 4), (3, 5)]), 1),
    (nx.DiGraph([(1, 2), (2, 3), (0, 1), (2, 4)]), 0),
])
def test_get_graph_root(graph, expected_root: str):
    observed_root = allocate.network.algorithms.get_graph_root(graph)
    assert observed_root == expected_root


@pytest.mark.parametrize('frame,expected_graph', [
    (
        pd.DataFrame([
            dict(label='0', desired_ratio=1.0e2, current_value=5500.0, update_amount=1.0, children=('X', 'Y', 'Z')),
            dict(label='X', desired_ratio=4.5e1, current_value=2500.0, update_amount=0.0, children=()),
            dict(label='Y', desired_ratio=2.0e1, current_value=5000.0, update_amount=0.0, children=()),
            dict(label='Z', desired_ratio=3.5e1, current_value=500.00, update_amount=0.0, children=()),
        ]),
        tests.utilities.make_graph(nodes=[
            ('0', dict(level=0, desired_ratio=1.00, current_value=5500.0, current_ratio=1.0000, update_amount=1.0)),
            ('X', dict(level=1, desired_ratio=0.45, current_value=2500.0, current_ratio=0.3125, update_amount=0.0)),
            ('Y', dict(level=1, desired_ratio=0.20, current_value=5000.0, current_ratio=0.6250, update_amount=0.0)),
            ('Z', dict(level=1, desired_ratio=0.35, current_value=500.00, current_ratio=0.0625, update_amount=0.0)),
        ], edges=[
            ('0', 'X'), ('0', 'Y'), ('0', 'Z')
        ]),
    )
])
def test_create(frame: pd.DataFrame, expected_graph: nx.DiGraph):
    logging.debug('starting_frame\n%s', frame)
    tests.utilities.show_graph('expected_graph', expected_graph)
    observed_graph: nx.DiGraph = allocate.network.algorithms.create(frame)
    tests.utilities.show_graph('observed_graph', observed_graph)
    attrs = ['level', 'desired_ratio', 'current_value', 'current_ratio', 'update_amount']
    value = [-100, -1000.0, -1000.0, -1000.0, -1000.0]
    node_match = nx.algorithms.isomorphism.numerical_node_match(attrs, value)
    assert nx.is_isomorphic(observed_graph, expected_graph, node_match=node_match)


@pytest.mark.parametrize('starting_graph,expected_graph,key,level', [
    (
        tests.utilities.make_graph(nodes=[
            ('0', dict(value=8.00)),
            ('A', dict(value=2.00)),
            ('B', dict(value=2.00)),
            ('C', dict(value=4.00)),
        ], edges=[
            ('0', 'A'), ('0', 'B'), ('0', 'C')
        ]),
        tests.utilities.make_graph(nodes=[
            ('0', dict(value=1.00)),
            ('A', dict(value=0.25)),
            ('B', dict(value=0.25)),
            ('C', dict(value=0.50)),
        ], edges=[
            ('0', 'A'), ('0', 'B'), ('0', 'C')
        ]),
        'value', None
    ),
    (
        tests.utilities.make_graph(nodes=[
            ('1', dict(value=8.00)),
            ('Q', dict(value=2.00)),
            ('R', dict(value=2.00)),
            ('S', dict(value=4.00)),
        ], edges=[
            ('1', 'Q'), ('1', 'R'), ('1', 'S')
        ]),
        tests.utilities.make_graph(nodes=[
            ('1', dict(value=1.00)),
            ('Q', dict(value=2.00)),
            ('R', dict(value=2.00)),
            ('S', dict(value=4.00)),
        ], edges=[
            ('1', 'Q'), ('1', 'R'), ('1', 'S')
        ]),
        'value', 0
    ),
])
def test_normalize(starting_graph: nx.DiGraph, expected_graph: nx.DiGraph, key: str, level: int):
    tests.utilities.show_graph('starting_graph', starting_graph)
    observed_graph: nx.DiGraph = allocate.network.algorithms.normalize(starting_graph, key, levels=level, inplace=True)
    tests.utilities.show_graph('expected_graph', expected_graph)
    tests.utilities.show_graph('observed_graph', observed_graph)
    node_match = nx.algorithms.isomorphism.numerical_node_match(key, 0.0)
    assert nx.is_isomorphic(starting_graph, starting_graph, node_match=node_match)
    assert nx.is_isomorphic(observed_graph, observed_graph, node_match=node_match)
    assert nx.is_isomorphic(expected_graph, expected_graph, node_match=node_match)
    assert nx.is_isomorphic(observed_graph, expected_graph, node_match=node_match)
    assert id(observed_graph) == id(starting_graph)
    assert id(observed_graph) != id(expected_graph)


@pytest.mark.parametrize('starting_graph,expected_graph,key,out', [
    (
        tests.utilities.make_graph(nodes=[
            ('1', dict(inp_value=0.50)),
            ('2', dict(inp_value=0.25)),
            ('3', dict(inp_value=0.50)),
            ('4', dict(inp_value=0.75)),
            ('5', dict(inp_value=0.10)),
            ('6', dict(inp_value=0.10)),
            ('7', dict(inp_value=0.10)),
        ], edges=[
            ('1', '2'), ('1', '3'), ('1', '4'), ('4', '5'), ('5', '6'), ('6', '7')
        ]),
        tests.utilities.make_graph(nodes=[
            ('1', dict(inp_value=0.50, out_value=0.50)),
            ('2', dict(inp_value=0.25, out_value=0.50 * 0.25)),
            ('3', dict(inp_value=0.50, out_value=0.50 * 0.50)),
            ('4', dict(inp_value=0.75, out_value=0.50 * 0.75)),
            ('5', dict(inp_value=0.10, out_value=0.50 * 0.10)),
            ('6', dict(inp_value=0.10, out_value=0.50 * 0.10 * 0.10)),
            ('7', dict(inp_value=0.20, out_value=0.50 * 0.10 * 0.10 * 0.10)),
        ], edges=[
            ('1', '2'), ('1', '3'), ('1', '4'), ('4', '5'), ('5', '6'), ('6', '7')
        ]),
        'inp_value', 'out_value'
    ),
])
def test_aggregate_quantity_along_depth(starting_graph: nx.DiGraph, expected_graph: nx.DiGraph, key: str, out: str):
    tests.utilities.show_graph('starting_graph', starting_graph, inp_value='{:.3f}')
    observed_graph: nx.DiGraph = \
        allocate.network.algorithms.aggregate_quantity_along_depth(starting_graph, key, out, inplace=True)
    tests.utilities.show_graph('expected_graph', expected_graph, inp_value='{:.3f}', out_value='{:.5f}')
    tests.utilities.show_graph('observed_graph', observed_graph, inp_value='{:.3f}', out_value='{:.5f}')
    node_match = nx.algorithms.isomorphism.numerical_node_match([key, out], [0.0, 0.0])
    assert nx.is_isomorphic(observed_graph, expected_graph, node_match=node_match)

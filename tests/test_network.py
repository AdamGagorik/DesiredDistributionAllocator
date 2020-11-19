"""
Unit tests for module.
"""
import networkx as nx
import unittest.mock
import logging
import pytest

import allocate.network


def make_graph(nodes: list, edges: list) -> nx.DiGraph:
    graph = nx.DiGraph()
    for node, kwargs in nodes:
        graph.add_node(node, **kwargs)
    for e1, e2 in edges:
        graph.add_edge(e1, e2)
    return graph


def test_create():
    pass


@pytest.mark.parametrize('graph,attrs', [
    (
        make_graph(nodes=[
            ('0', dict(value=8.00)),
            ('A', dict(value=2.00)),
            ('B', dict(value=2.00)),
            ('C', dict(value=4.00)),
            ('D', dict(value=4.00)),
            ('E', dict(value=4.00)),
        ], edges=[
            ('0', 'A'), ('0', 'B'), ('0', 'C'), ('C', 'D'), ('C', 'E')
        ]),
        dict(value='{:.3f}', other='{:.3f}')
    ),
])
def test_display(graph: nx.DiGraph, attrs: dict):
    logging.debug('\n%s', allocate.network.display(graph, **attrs))


def test_validate():
    with \
        unittest.mock.patch.object(
            nx, 'is_directed_acyclic_graph', return_value=True) as mock_0, \
        unittest.mock.patch.object(
            allocate.network, 'network_has_no_cycles', return_value=True) as mock_1, \
        unittest.mock.patch.object(
            allocate.network, 'network_has_no_orphan_children', return_value=True) as mock_2, \
        unittest.mock.patch.object(
            allocate.network, 'network_children_only_have_single_parent', return_value=True) as mock_3, \
        unittest.mock.patch.object(
            allocate.network, 'network_sums_to_100_percent_at_each_level', return_value=True) as mock_4:
        allocate.network.validate(nx.DiGraph())
        mock_0.assert_called_once()
        mock_1.assert_called_once()
        mock_2.assert_called_once()
        mock_3.assert_called_once()
        mock_4.assert_called_once()


@pytest.mark.parametrize('starting_graph,expected_graph,key,level', [
    (
        make_graph(nodes=[
            ('0', dict(value=8.00)),
            ('A', dict(value=2.00)),
            ('B', dict(value=2.00)),
            ('C', dict(value=4.00)),
        ], edges=[
            ('0', 'A'), ('0', 'B'), ('0', 'C')
        ]),
        make_graph(nodes=[
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
        make_graph(nodes=[
            ('0', dict(value=8.00)),
            ('A', dict(value=2.00)),
            ('B', dict(value=2.00)),
            ('C', dict(value=4.00)),
        ], edges=[
            ('0', 'A'), ('0', 'B'), ('0', 'C')
        ]),
        make_graph(nodes=[
            ('0', dict(value=1.00)),
            ('A', dict(value=2.00)),
            ('B', dict(value=2.00)),
            ('C', dict(value=4.00)),
        ], edges=[
            ('0', 'A'), ('0', 'B'), ('0', 'C')
        ]),
        'value', 0
    ),
])
def test_normalize(starting_graph: nx.DiGraph, expected_graph: nx.DiGraph, key: str, level: int):
    logging.debug('starting_graph\n%s', allocate.network.display(starting_graph, value='{:.2f}'))
    observed_graph: nx.DiGraph = allocate.network.normalize(starting_graph, key, level, inplace=True)
    logging.debug('observed_graph\n%s', allocate.network.display(observed_graph, value='{:.2f}'))
    logging.debug('expected_graph\n%s', allocate.network.display(expected_graph, value='{:.2f}'))
    node_match = nx.algorithms.isomorphism.numerical_node_match(key, 0.0)
    assert nx.is_isomorphic(starting_graph, starting_graph, node_match=node_match)
    assert nx.is_isomorphic(observed_graph, observed_graph, node_match=node_match)
    assert nx.is_isomorphic(expected_graph, expected_graph, node_match=node_match)
    assert nx.is_isomorphic(observed_graph, expected_graph, node_match=node_match)
    assert id(observed_graph) == id(starting_graph)
    assert id(observed_graph) != id(expected_graph)


@pytest.mark.parametrize('graph,expected_root', [
    (nx.DiGraph([(1, 2), (2, 3), (3, 4), (3, 5)]), 1),
    (nx.DiGraph([(1, 2), (2, 3), (0, 1), (2, 4)]), 0),
])
def test_get_graph_root(graph, expected_root: str):
    observed_root = allocate.network.get_graph_root(graph)
    assert observed_root == expected_root


@pytest.mark.parametrize('graph,expected_valid', [
    (nx.DiGraph([(1, 2), (2, 3), (3, 4)]), True),
    (nx.DiGraph([(1, 2), (2, 3), (3, 1)]), False),
])
def test_network_has_no_cycles(graph: nx.DiGraph, expected_valid: bool):
    observed_valid: bool = allocate.network.network_has_no_cycles(graph)
    assert observed_valid == expected_valid


@pytest.mark.parametrize('graph,expected_valid', [
    (nx.DiGraph({0: [1, 2], 3: [0]}), True),
    (nx.DiGraph({0: [1, 2], 3: [4]}), False),
])
def test_network_has_no_orphan_children(graph: nx.DiGraph, expected_valid: bool):
    observed_valid: bool = allocate.network.network_has_no_orphan_children(graph)
    assert observed_valid == expected_valid


@pytest.mark.parametrize('graph,expected_valid', [
    (nx.DiGraph([(1, 2), (1, 3), (1, 4)]), True),
    (nx.DiGraph([(1, 2), (1, 3), (4, 2)]), False),
])
def test_network_children_only_have_single_parent(graph: nx.DiGraph, expected_valid: bool):
    observed_valid: bool = allocate.network.network_children_only_have_single_parent(graph)
    assert observed_valid == expected_valid


@pytest.mark.parametrize('graph,key,expected_valid', [
    (
        make_graph(nodes=[
            ('0', dict(value=100.0)),
            ('A', dict(value=40.0)),
            ('B', dict(value=25.0)),
            ('C', dict(value=35.0)),
        ], edges=[
            ('0', 'A'), ('0', 'B'), ('0', 'C')
        ]), 'value', True
    ),
    (
        make_graph(nodes=[
            ('0', dict(value=100.0)),
            ('A', dict(value=100.0)),
            ('B', dict(value=100.0)),
            ('C', dict(value=100.0)),
        ], edges=[
            ('0', 'A'), ('0', 'B'), ('0', 'C')
        ]), 'value', False
    ),
    (
        make_graph(nodes=[
            ('0', dict(value=100.0)),
            ('A', dict(value=10.0)),
            ('B', dict(value=10.0)),
            ('C', dict(value=10.0)),
        ], edges=[
            ('0', 'A'), ('0', 'B'), ('0', 'C')
        ]), 'value', False
    ),
])
def test_network_sums_to_100_percent_at_each_level(graph: nx.DiGraph, key: str, expected_valid: bool):
    observed_valid: bool = allocate.network.network_sums_to_100_percent_at_each_level(graph, key)
    assert observed_valid == expected_valid

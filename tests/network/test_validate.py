"""
Unit tests for module.
"""
import networkx as nx
import unittest.mock
import pytest

import allocate.network.validate
import tests.utilities


def test_validate():
    mock_g = nx.DiGraph()
    mock_a = unittest.mock.MagicMock(return_value=True)
    mock_b = unittest.mock.MagicMock(return_value=True)
    assert allocate.network.validate.validate(mock_g, mock_a, mock_b)
    mock_a.assert_called_once_with(mock_g)
    mock_b.assert_called_once_with(mock_g)


@pytest.mark.parametrize('graph,expected_valid', [
    (nx.DiGraph([(1, 2), (2, 3), (3, 4)]), True),
    (nx.DiGraph([(1, 2), (2, 3), (3, 1)]), False),
])
def test_network_has_no_cycles(graph: nx.DiGraph, expected_valid: bool):
    observed_valid: bool = allocate.network.validate.network_has_no_cycles(graph)
    assert observed_valid == expected_valid


@pytest.mark.parametrize('graph,expected_valid', [
    (nx.DiGraph({0: [1, 2], 3: [0]}), True),
    (nx.DiGraph({0: [1, 2], 3: [4]}), False),
])
def test_network_has_no_orphan_children(graph: nx.DiGraph, expected_valid: bool):
    observed_valid: bool = allocate.network.validate.network_has_no_orphan_children(graph)
    assert observed_valid == expected_valid


@pytest.mark.parametrize('graph,expected_valid', [
    (nx.DiGraph([(1, 2), (1, 3), (1, 4)]), True),
    (nx.DiGraph([(1, 2), (1, 3), (4, 2)]), False),
])
def test_network_children_only_have_single_parent(graph: nx.DiGraph, expected_valid: bool):
    observed_valid: bool = allocate.network.validate.network_children_only_have_single_parent(graph)
    assert observed_valid == expected_valid


@pytest.mark.parametrize('graph,key,expected_valid', [
    (
        tests.utilities.make_graph(nodes=[
            ('0', dict(value=1.00)),
            ('A', dict(value=0.40)),
            ('B', dict(value=0.25)),
            ('C', dict(value=0.35)),
        ], edges=[
            ('0', 'A'), ('0', 'B'), ('0', 'C')
        ]), 'value', True
    ),
    (
        tests.utilities.make_graph(nodes=[
            ('0', dict(value=100.0)),
            ('A', dict(value=100.0)),
            ('B', dict(value=100.0)),
            ('C', dict(value=100.0)),
        ], edges=[
            ('0', 'A'), ('0', 'B'), ('0', 'C')
        ]), 'value', False
    ),
    (
        tests.utilities.make_graph(nodes=[
            ('0', dict(value=100.0)),
            ('A', dict(value=0.1)),
            ('B', dict(value=0.1)),
            ('C', dict(value=0.1)),
        ], edges=[
            ('0', 'A'), ('0', 'B'), ('0', 'C')
        ]), 'value', False
    ),
])
def test_network_sums_to_100_percent_at_each_level(graph: nx.DiGraph, key: str, expected_valid: bool):
    observed_valid: bool = allocate.network.validate.network_sums_to_100_percent_at_each_level(graph, key)
    assert observed_valid == expected_valid

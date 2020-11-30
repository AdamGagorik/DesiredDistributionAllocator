"""
Unit tests for module.
"""
import networkx as nx
import pandas as pd
import logging
import pytest

import allocate.plotting.node_attr_table
import tests.utilities
import pandas.testing


@pytest.fixture()
def starting_graph() -> nx.DiGraph:
    graph: nx.DiGraph = tests.utilities.make_graph(nodes=[
        ('A', dict(a=1, b=0.01, c=1.0)),
        ('B', dict(a=2, b=0.02, c=2.0)),
        ('C', dict(a=3, b=0.03, c=3.0)),
        ('D', dict(a=4, b=0.04, c=4.0)),
        ('E', dict(a=5, b=0.05, c=5.0)),
        ('F', dict(a=6, b=0.06, c=6.0)),
    ], edges=[('A', 'B'), ('A', 'C'), ('C', 'D'), ('D', 'E'), ('D', 'F')])
    yield graph


@pytest.fixture()
def expected_frame() -> pd.DataFrame:
    frame: pd.DataFrame = pd.DataFrame([
        dict(g_id=0, node='A', a=1, b=0.01, c=1.0, level=0),
        dict(g_id=0, node='B', a=2, b=0.02, c=2.0, level=1),
        dict(g_id=0, node='C', a=3, b=0.03, c=3.0, level=1),
        dict(g_id=0, node='D', a=4, b=0.04, c=4.0, level=2),
        dict(g_id=0, node='E', a=5, b=0.05, c=5.0, level=3),
        dict(g_id=0, node='F', a=6, b=0.06, c=6.0, level=3),
    ])
    yield frame


@pytest.mark.parametrize('vdims', [
    None, ['a'], ['a', 'c'], ['q']
])
def test_create(vdims: list, starting_graph: nx.DiGraph, expected_frame: pd.DataFrame):
    # special logic for expected frame
    if vdims is not None:
        expected_vdims = ['g_id', 'node']
        for vdim in vdims:
            if vdim in ['a', 'b', 'c']:
                expected_vdims.append(vdim)
            else:
                # unknown node attributes expected to be None
                expected_frame[vdim] = None
                expected_vdims.append(vdim)
        # dynamically added column is expected
        expected_vdims.append('level')
        expected_frame = expected_frame[expected_vdims]

    tests.utilities.show_graph('starting_graph', starting_graph)
    logging.debug('expected_frame\n%s', expected_frame)

    add_properties = dict(level=lambda g, n: nx.shortest_path_length(g, 'A', n))
    observed_frame: pd.DataFrame = allocate.plotting.node_attr_table.create(
        starting_graph, vdims=vdims, add_properties=add_properties)

    logging.debug('observed_frame\n%s', observed_frame)
    pandas.testing.assert_frame_equal(expected_frame, observed_frame)


@pytest.mark.parametrize('unstack', [
    False, True
])
def test_create_multiple(unstack: bool, starting_graph: nx.DiGraph, expected_frame: pd.DataFrame):
    tests.utilities.show_graph('starting_graph', starting_graph)

    # the same graph is passed 3 times
    expected_frame = pd.concat([
        expected_frame.assign(g_id=0),
        expected_frame.assign(g_id=1),
        expected_frame.assign(g_id=2),
    ], ignore_index=True)
    logging.debug('expected_frame\n%s', expected_frame)

    add_properties = dict(level=lambda g, n: nx.shortest_path_length(g, 'A', n))
    observed_frame: pd.DataFrame = allocate.plotting.node_attr_table.create(
        starting_graph, starting_graph, starting_graph, add_properties=add_properties)

    logging.debug('observed_frame\n%s', observed_frame)
    pandas.testing.assert_frame_equal(expected_frame, observed_frame)

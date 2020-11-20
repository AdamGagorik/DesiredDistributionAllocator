"""
Unit tests for module.
"""
import networkx as nx
import logging
import pytest

import allocate.network.visualize
import tests.utilities


@pytest.mark.parametrize('graph,attrs', [
    (
        tests.utilities.make_graph(nodes=[
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
def test_text(graph: nx.DiGraph, attrs: dict):
    logging.debug('\n%s', allocate.network.visualize.text(graph, **attrs))

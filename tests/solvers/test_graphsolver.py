"""
Unit tests for module.
"""
import networkx as nx
import pandas as pd
import logging
import pytest

import allocate.solvers.graphsolver
import allocate.network.algorithms
import allocate.network.visualize
import tests.utilities

from allocate.solvers.constrained import BucketSolverConstrained
from allocate.solvers.constrained import BucketSolverSimple
from allocate.solvers import BucketSolver


@pytest.mark.parametrize('starting_frame,expected_graph,solver', [
    (
        pd.DataFrame([
            dict(label='T', current_value=3000.0, optimal_ratio=1.00, amount_to_add=0.0000, children=('H', 'I', 'J')),
            dict(label='H', current_value=3000.0, optimal_ratio=0.50, amount_to_add=0.0000, children=()),
            dict(label='I', current_value=0000.0, optimal_ratio=0.35, amount_to_add=0.0000, children=()),
            dict(label='J', current_value=0000.0, optimal_ratio=0.15, amount_to_add=0.0000, children=()),
        ]),
        tests.utilities.make_graph(nodes=[
            ('T', dict(results_value=3000.0 + 3000.0 * 0.00, amount_to_add=+3000.0 * 0.00)),
            ('H', dict(results_value=3000.0 - 3000.0 * 0.50, amount_to_add=-3000.0 * 0.50)),
            ('I', dict(results_value=0.0000 + 3000.0 * 0.35, amount_to_add=+3000.0 * 0.35)),
            ('J', dict(results_value=0.0000 + 3000.0 * 0.15, amount_to_add=+3000.0 * 0.15)),
        ], edges=[
            ('T', 'H'), ('T', 'I'), ('T', 'J')
        ]),
        BucketSolverSimple
    ),
    (
        pd.DataFrame([
            dict(label='A', current_value=4000.0, optimal_ratio=1.00, amount_to_add=1000.0, children=('0', '1', '2')),
            dict(label='0', current_value=2000.0, optimal_ratio=0.50, amount_to_add=0.0000, children=()),
            dict(label='1', current_value=1000.0, optimal_ratio=0.25, amount_to_add=0.0000, children=()),
            dict(label='2', current_value=1000.0, optimal_ratio=0.25, amount_to_add=0.0000, children=()),
        ]),
        tests.utilities.make_graph(nodes=[
            ('A', dict(results_value=4000.0 + 1000.0 * 1.00, amount_to_add=1000.0 * 0.00)),
            ('0', dict(results_value=2000.0 + 1000.0 * 0.50, amount_to_add=1000.0 * 0.50)),
            ('1', dict(results_value=1000.0 + 1000.0 * 0.25, amount_to_add=1000.0 * 0.25)),
            ('2', dict(results_value=1000.0 + 1000.0 * 0.25, amount_to_add=1000.0 * 0.25)),
        ], edges=[
            ('A', '0'), ('A', '1'), ('A', '2')
        ]),
        BucketSolverConstrained
    ),
    (
        pd.DataFrame([
            dict(label='B', current_value=8000.0, optimal_ratio=1.00, amount_to_add=4000.0, children=('3', '4', '5')),
            dict(label='3', current_value=4000.0, optimal_ratio=0.50, amount_to_add=0.0000, children=()),
            dict(label='4', current_value=2000.0, optimal_ratio=0.25, amount_to_add=0.0000, children=()),
            dict(label='5', current_value=2000.0, optimal_ratio=0.25, amount_to_add=0.0000, children=('C', 'D')),
            dict(label='C', current_value=1000.0, optimal_ratio=0.50, amount_to_add=0.0000, children=()),
            dict(label='D', current_value=1000.0, optimal_ratio=0.50, amount_to_add=0.0000, children=('6', '7')),
            dict(label='6', current_value=2.50e2, optimal_ratio=0.25, amount_to_add=0.0000, children=()),
            dict(label='7', current_value=7.50e2, optimal_ratio=0.75, amount_to_add=0.0000, children=()),
        ]),
        tests.utilities.make_graph(nodes=[
            ('B', dict(results_value=8000.0 + 4000.0 * 1.00 * 1.00 * 1.00, amount_to_add=4000.0 * 0.00 * 1.00 * 1.00)),
            ('3', dict(results_value=4000.0 + 4000.0 * 0.50 * 1.00 * 1.00, amount_to_add=4000.0 * 0.50 * 1.00 * 1.00)),
            ('4', dict(results_value=2000.0 + 4000.0 * 0.25 * 1.00 * 1.00, amount_to_add=4000.0 * 0.25 * 1.00 * 1.00)),
            ('5', dict(results_value=2000.0 + 4000.0 * 0.25 * 1.00 * 1.00, amount_to_add=4000.0 * 0.00 * 1.00 * 1.00)),
            ('C', dict(results_value=1000.0 + 4000.0 * 0.25 * 0.50 * 1.00, amount_to_add=4000.0 * 0.25 * 0.50 * 1.00)),
            ('D', dict(results_value=1000.0 + 4000.0 * 0.25 * 0.50 * 1.00, amount_to_add=4000.0 * 0.00 * 0.50 * 1.00)),
            ('6', dict(results_value=2.50e2 + 4000.0 * 0.25 * 0.50 * 0.25, amount_to_add=4000.0 * 0.25 * 0.50 * 0.25)),
            ('7', dict(results_value=7.50e2 + 4000.0 * 0.25 * 0.50 * 0.75, amount_to_add=4000.0 * 0.25 * 0.50 * 0.75)),
        ], edges=[
            ('B', '3'), ('B', '4'), ('B', '5'), ('5', 'C'), ('5', 'D'), ('D', '6'), ('D', '7')
        ]),
        BucketSolverConstrained
    ),
], ids=[
    'simple_no_addition',
    'constrained_simple',
    'constrained_complex',
])
def test_solve(starting_frame: pd.DataFrame, expected_graph: nx.DiGraph, solver: BucketSolver):
    logging.debug('starting_frame:\n%s', starting_frame)
    starting_graph: nx.DiGraph = allocate.network.algorithms.create(starting_frame)
    tests.utilities.show_graph('starting_graph', starting_graph, **allocate.network.visualize.formats_inp)
    tests.utilities.show_graph('expected_graph', expected_graph, **allocate.network.visualize.formats_out)
    observed_graph: nx.DiGraph = allocate.solvers.graphsolver.solve(starting_graph, solver=solver, inplace=False)
    tests.utilities.show_graph('observed_graph', observed_graph, **allocate.network.visualize.formats_out)
    node_match = nx.algorithms.isomorphism.numerical_node_match(
        ['results_value', 'amount_to_add'], [-1000, -1000])
    assert nx.is_isomorphic(observed_graph, expected_graph, node_match=node_match)

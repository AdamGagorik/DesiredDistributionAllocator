"""
A script to allocate items to reach the desired distribution.
"""
import networkx as nx
import pandas as pd
import argparse
import logging
import os

import allocate.configure
import allocate.utilities
import allocate.load_inputs
import allocate.network.visualize
import allocate.network.algorithms

import allocate.solvers.montecarlo
import allocate.solvers.graphsolver
import allocate.solvers.constrained
import allocate.solvers.unconstrained

from allocate.network.attributes import node_attrs


# noinspection DuplicatedCode
def get_arguments(args=None) -> argparse.Namespace:
    """
    Get the command line arguments.
    """
    # noinspection PyTypeChecker
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--config', default='allocate.yaml', type=os.path.abspath,
                        help='The config file to load and process')
    parser.add_argument('--constrained', dest='constrained', action='store_true',
                        help='do not allow values to be removed from bins')
    parser.add_argument('--monte-carlo', dest='monte_carlo', action='store_true',
                        help='use the Monte Carlo based constrained solver')
    parser.add_argument('--step-size', dest='step_size', type=float, default=0.01,
                        help='The Monte Carlo step size to use')
    return parser.parse_args(args=args)


def main(config: str, constrained: bool, monte_carlo: bool, step_size: float):
    """
    The main logic of the script.
    """
    logging.debug('input: %s', config)

    frame: pd.DataFrame = allocate.load_inputs.load(path=config)
    logging.debug('frame:\n%s\n', frame)

    graph: nx.DiGraph = allocate.network.algorithms.create(frame)
    logging.debug('graph:\n%s', allocate.network.visualize.text(graph, **allocate.network.visualize.formats_inp))

    if monte_carlo:
        kwargs = dict(step_size=step_size)
        solver = allocate.solvers.montecarlo.BucketSolverConstrainedMonteCarlo
    elif constrained:
        kwargs = dict()
        solver = allocate.solvers.constrained.BucketSolverConstrained
    else:
        kwargs = dict()
        solver = allocate.solvers.constrained.BucketSolverSimple

    # noinspection PyTypeChecker
    solve: nx.DiGraph = allocate.solvers.graphsolver.solve(graph, inplace=False, solver=solver, **kwargs)
    logging.debug('solved:\n%s', allocate.network.visualize.text(solve, **allocate.network.visualize.formats_out))
    display_results(solve, kvfmt='%-{}s: %s'.format(max(15, max(len(n) for n in solve.nodes))))


def display_results(graph: nx.DiGraph, kvfmt: str = '%-20s: %s'):
    amount_to_add: float = allocate.network.algorithms.aggregate_quantity(
        graph, key=node_attrs.amount_to_add.column)
    logging.debug(kvfmt, 'amount_to_add', allocate.utilities.moneyfmt(amount_to_add))

    results_value: float = allocate.network.algorithms.aggregate_quantity(
        graph, key=node_attrs.results_value.column, leaves=True)
    logging.debug(kvfmt, 'results_value', allocate.utilities.moneyfmt(results_value))

    results_ratio: float = allocate.network.algorithms.aggregate_quantity(
        graph, key=node_attrs.results_ratio.column, leaves=True)
    logging.debug(kvfmt, 'results_ratio', allocate.utilities.moneyfmt(results_ratio, decimals=10))

    logging.debug('')
    for node in graph:
        # noinspection PyCallingNonCallable
        if graph.out_degree(node) == 0 and graph.in_degree(node) == 1:
            amount_to_add: float = graph.nodes[node][node_attrs.amount_to_add.column]
            logging.debug(kvfmt, node, allocate.utilities.moneyfmt(amount_to_add))


if __name__ == '__main__':
    # noinspection PyBroadException
    try:
        allocate.configure.pandas()
        allocate.configure.logging()
        opts = get_arguments()
        main(**opts.__dict__)
    except Exception:
        logging.exception('caught unhandled exception!')
        exit(-1)
    exit(0)

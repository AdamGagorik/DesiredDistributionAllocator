"""
Solve the bucket problem over a hierarchy of buckets.

For example, given the following input::

A    level=[0] current_value=[ 4,000.00] optimal_ratio=[1.000] amount_to_add=[ 1,000.00]
 ├─0 level=[1] current_value=[ 2,000.00] optimal_ratio=[0.500] amount_to_add=[     0.00]
 ├─1 level=[1] current_value=[ 1,000.00] optimal_ratio=[0.250] amount_to_add=[     0.00]
 └─2 level=[1] current_value=[ 1,000.00] optimal_ratio=[0.250] amount_to_add=[     0.00]

Compute the amount to add to each bucket::

A    level=[0] results_value=[ 5,000.00] results_ratio=[1.000] amount_to_add=[     0.00]
 ├─0 level=[1] results_value=[ 2,500.00] results_ratio=[0.500] amount_to_add=[   500.00]
 ├─1 level=[1] results_value=[ 1,250.00] results_ratio=[0.250] amount_to_add=[   250.00]
 └─2 level=[1] results_value=[ 1,250.00] results_ratio=[0.250] amount_to_add=[   250.00]
"""
import networkx as nx
import copy

from allocate.solvers.constrained import BucketSolverConstrained
from allocate.solvers import BucketSolver

from allocate.network.attributes import node_attrs
import allocate.network.algorithms


def solve(graph: nx.DiGraph, solver: BucketSolver = BucketSolverConstrained,
          inplace: bool = False, max_attempts: int = 1024, **kwargs) -> nx.DiGraph:
    """
    Solve the bucket problem over a hierarchy of buckets.

    Parameters:
        graph: The DAG to process.
        solver: The bucket solver during traversal.
        inplace: Should the operation happen in place or on a copy?
        max_attempts: The maximum allowed passes through the network.
        **kwargs: Extra key word arguments to the solver's solve method.

    Returns:
        The modified graph, with the results_value and results_delta updated.
    """
    if not inplace:
        graph = copy.deepcopy(graph)

    source = allocate.network.algorithms.get_graph_root(graph)
    for attempt in range(max_attempts):
        stop_algorithm = True
        # walk the graph from the bottom up, solving the bucket problem set of children
        for parent, children in reversed(list(nx.bfs_successors(graph, source))):
            amount_to_add = graph.nodes[parent][node_attrs.amount_to_add.column]
            if amount_to_add > 0:
                current_values = [graph.nodes[n][node_attrs.current_value.column] for n in children]
                optimal_ratios = [graph.nodes[n][node_attrs.optimal_ratio.column] for n in children]
                stop_algorithm = False
                # solve the bucket problem over the children
                system = allocate.solvers.BucketSystem.create(
                    amount_to_add=amount_to_add, current_values=current_values,
                    optimal_ratios=optimal_ratios, labels=children)
                solved = solver.solve(system, **kwargs)
                # negate the amount to add so we dont try to add it again on the next pass
                graph.nodes[parent][node_attrs.amount_to_add.column] = -amount_to_add
                # increment the amount to add value for the children of this node
                for i, child in enumerate(children):
                    graph.nodes[child][node_attrs.amount_to_add.column] += solved.result_delta.values[i]
        if stop_algorithm:
            break
    else:
        raise RuntimeError('max attempts reached in network solver!')

    # finalize the amounts to add and the results_value column
    for node in graph:
        graph.nodes[node][node_attrs.amount_to_add.column] = abs(graph.nodes[node][node_attrs.amount_to_add.column])
        graph.nodes[node][node_attrs.results_value.column] = \
            graph.nodes[node][node_attrs.current_value.column] + \
            graph.nodes[node][node_attrs.amount_to_add.column]

        # noinspection PyCallingNonCallable
        if graph.out_degree(node):
            graph.nodes[node][node_attrs.amount_to_add.column] = 0

    # calculate the final ratios for the results column
    graph = allocate.network.algorithms.normalize(
        graph, inplace=True,
        key=allocate.network.attributes.node_attrs.results_value.column,
        out=allocate.network.attributes.node_attrs.results_ratio.column)

    return graph

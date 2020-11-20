"""
Methods for creating a graph representation of the problem.
"""
import networkx.exception
import networkx as nx
import pandas as pd
import functools
import operator
import typing
import copy

import allocate.network.attributes
import allocate.network.validate


def get_graph_root(graph: nx.DiGraph) -> typing.Any:
    """
    Assume the graph is a rooted tree and find the root node.
    """
    for n in nx.topological_sort(graph):
        return n


def create(frame: pd.DataFrame) -> nx.DiGraph:
    """
    Transform the input data into a graph object.

    Parameters:
        frame: A dataframe with the data to build the DAG.

    Returns:
        The graph that was constructed.
    """
    attrs = [
        f for f in allocate.network.attributes.node_attrs.subset() if f.column not in [
            allocate.network.attributes.node_attrs.label,
            allocate.network.attributes.node_attrs.level,
        ]
    ]

    graph = nx.DiGraph()
    for index, data in frame.iterrows():
        label = data[allocate.network.attributes.node_attrs.label.column]
        graph.add_node(label, **{
            attr.column: data.get(attr.column, default=attr.value) for attr in attrs
        })

    for index, data in frame.iterrows():
        label = data[allocate.network.attributes.node_attrs.label.column]
        for child in data.get('children', default=()):
            if label not in graph or child not in graph:
                raise ValueError(f'can not create edge with missing nodes! {label} -> {child}')
            else:
                graph.add_edge(label, child)

    source = get_graph_root(graph)
    depths = networkx.single_source_shortest_path_length(graph, source)
    for label, level in depths.items():
        graph.nodes[label].update(level=level)

    if not allocate.network.validate.validate(
            graph,
            nx.algorithms.is_directed_acyclic_graph,
            allocate.network.validate.network_has_no_cycles,
            allocate.network.validate.network_has_no_orphan_children,
            allocate.network.validate.network_children_only_have_single_parent
    ):
        raise ValueError('invalid network')

    # normalize desired ratio
    graph = normalize(graph, inplace=True,
                      key=allocate.network.attributes.node_attrs.desired_ratio.column,
                      out=allocate.network.attributes.node_attrs.desired_ratio.column)

    # calculate current ratio
    graph = normalize(graph, inplace=True,
                      key=allocate.network.attributes.node_attrs.current_value.column,
                      out=allocate.network.attributes.node_attrs.current_ratio.column)

    if not allocate.network.validate.validate(
            graph,
            lambda g: allocate.network.validate.network_sums_to_100_percent_at_each_level(
                g, allocate.network.attributes.node_attrs.desired_ratio.column, 1.0),
            lambda g: allocate.network.validate.network_sums_to_100_percent_at_each_level(
                g, allocate.network.attributes.node_attrs.current_ratio.column, 1.0)
    ):
        raise ValueError('invalid network')

    return graph


def normalize(graph: nx.DiGraph, key: str, out: str = None,
              levels: typing.Union[int, typing.List[int], None] = None,
              inplace: bool = True) -> nx.DiGraph:
    """
    Make it so the amounts at each level sum to 100 percent.

    Parameters:
        graph: The DAG to normalize.
        key: The name of the attribute to normalize.
        out: The name of the attribute to store results under.
        levels: The level(s) of the tree to operate on or None to normalize attrs levels.
        inplace: Should the operation happen in place or on a copy?

    Returns:
        The modified graph, with the value normalized.
    """
    out = out if out is not None else key

    if not inplace:
        graph = copy.deepcopy(graph)

    if isinstance(levels, int):
        levels = [levels]

    source = get_graph_root(graph)
    values = nx.get_node_attributes(graph, key)
    depths = networkx.single_source_shortest_path_length(graph, source)
    dframe = pd.DataFrame(depths, index=['level']).T

    if levels is not None:
        dframe = dframe[dframe['level'].isin(levels)]

    if not dframe.empty:
        for level, group in dframe.groupby(by='level'):
            group['values'] = group.index.map(values)
            total = group['values'].sum()
            if total > 0:
                group['normed'] = group['values'] / total
            else:
                group['normed'] = 0.0

            for n, d in group.iterrows():
                graph.nodes[n][out] = d['normed']

    return graph


def aggregate_quantity(graph: nx.DiGraph, key: str, reduce: typing.Callable = operator.add) -> typing.Any:
    """
    Traverse the graph, reducing the node quantity at the key.

    Parameters:
        graph: The DAG to traverse.
        key: The name of the node attribute to aggregate.
        reduce: A function taking two values and returning one value.

    Returns:
        The value of the aggregated quantity.
    """
    return functools.reduce(reduce, nx.get_node_attributes(graph, key).values())


def aggregate_quantity_along_depth(graph: nx.DiGraph, key: str, out: str = None,
                                   reduce: typing.Callable = operator.mul, inplace: bool = True) -> nx.DiGraph:
    """
    Traverse the graph in a depth first manner, reducing the node quantity at the key.

    Parameters:
        graph: The DAG to traverse.
        key: The name of the node attribute to aggregate.
        out: The name of the node attribute to store results under.
        reduce: A function taking two values and returning one value.
        inplace: Should the operation happen in place or on a copy?

    Returns:
        The modified graph, with the value normalized.
    """
    out = out if out is not None else key

    if not inplace:
        graph = copy.deepcopy(graph)

    for e1, e2 in nx.dfs_edges(graph, source=get_graph_root(graph)):
        v0 = graph.nodes[e1].get(key, 1.)
        v1 = graph.nodes[e1].get(out, v0)
        v2 = graph.nodes[e2].get(key, 1.)
        graph.nodes[e1][out] = v1
        graph.nodes[e2][out] = reduce(v1, v2)

    return graph

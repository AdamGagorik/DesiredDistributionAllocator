"""
Methods for creating a graph representation of the problem.
"""
import networkx.exception
import networkx as nx
import pandas as pd
import numpy as np
import dataclasses
import logging
import typing
import copy
import io

from .attributes import node_attrs


def create(frame: pd.DataFrame) -> nx.DiGraph:
    """
    Transform the input data into a graph object.

    Parameters:
        frame: A dataframe with the data to build the DAG.

    Returns:
        The graph that was constructed.
    """
    attrs = [
        node_attrs.desired_ratio,
        node_attrs.current_value,
        node_attrs.current_ratio,
        node_attrs.update_amount,
    ]

    graph = nx.DiGraph()
    for index, data in frame.iterrows():
        label = data[node_attrs.label.column]
        graph.add_node(label, **{
            attr.column: data.get(attr.column, default=attr.value) for attr in attrs
        })

    for index, data in frame.iterrows():
        label = data[node_attrs.label.column]
        for child in data.get('children', default=()):
            if label not in graph or child not in graph:
                raise ValueError(f'can not create edge with missing nodes! {label} -> {child}')
            else:
                graph.add_edge(label, child)

    source = get_graph_root(graph)
    depths = networkx.single_source_shortest_path_length(graph, source)
    for label, level in depths.items():
        graph.nodes[label].update(level=level)

    graph = normalize(graph, inplace=True, key=node_attrs.desired_ratio.column)
    graph = normalize(graph, inplace=True, key=node_attrs.current_value.column, out=node_attrs.current_ratio.column)

    if not validate(graph):
        raise RuntimeError('graph is invalid!')

    return graph


def display(graph: nx.DiGraph, attrs: bool = False, **kwargs) -> str:
    """
    Display the graph using ASCII art.

    Parameters:
        graph: The DAG to display with ASCII art.
        attrs: Display all node attributes for nodes?
        kwargs: Node attributes to display and their format strings.

    Returns:
        The graph formatted as an ASCII string.
    """
    source = get_graph_root(graph)
    if attrs:
        return ASCIIDisplay(graph=graph, attrs=True)(source)
    else:
        return ASCIIDisplay(graph=graph, attrs=kwargs)(source)


def validate(graph: nx.DiGraph) -> bool:
    """
    Ensure consistency of the graph and enforce constraints of this problem.

    For example, perform the following transformation::

        0 value=8.00
         ├─A value=2.00
         ├─B value=2.00
         └─C value=4.00

        0 value=1.00
         ├─A value=0.25
         ├─B value=0.25
         └─C value=0.50

    Parameters:
        graph: The DAG to validate.

    Returns:
        True if the DAG is valid.
    """
    valid = True
    for validator in [
        network_has_no_cycles,
        nx.is_directed_acyclic_graph,
        network_has_no_orphan_children,
        network_children_only_have_single_parent,
        lambda g: network_sums_to_100_percent_at_each_level(g, node_attrs.desired_ratio.column),
    ]:
        if not validator(graph):
            valid = False
    return valid


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


def get_graph_root(graph: nx.DiGraph) -> typing.Any:
    """
    Assume the graph is a rooted tree and find the root node.
    """
    for n in nx.topological_sort(graph):
        return n


def network_has_no_cycles(graph: nx.DiGraph) -> bool:
    """
    The network is a directed acyclic graph?
    """
    try:
        cycle = nx.algorithms.find_cycle(graph, orientation='ignore')
        logging.error('network cycle found!')
        for edge in cycle:
            logging.error('edge: %s -> %s', *edge[:2])
        return False
    except networkx.exception.NetworkXNoCycle:
        return True


def network_has_no_orphan_children(graph: nx.DiGraph) -> bool:
    """
    All children in the network have a parent?
    """
    graph = graph.to_undirected(as_view=True)
    connected = nx.is_connected(graph)
    if not connected:
        logging.error('network is not connected!')
        for subgraph in nx.connected_components(graph):
            logging.error('sub graph: %s', subgraph)
        return False
    else:
        return True


def network_children_only_have_single_parent(graph: nx.DiGraph) -> bool:
    """
    All children in the network have a single parent?
    """
    valid = True
    if len(graph) > 1:
        # noinspection PyTypeChecker
        for n, degree in graph.in_degree:
            if degree > 1:
                logging.error('degree %d > 1 for node: %s', degree, n)
                valid = False

    if not valid:
        logging.error('nodes have multiple predecessors!')

    return valid


def network_sums_to_100_percent_at_each_level(graph: nx.DiGraph, key: str, expected: float = 1.0) -> bool:
    """
    The fraction desired at each level sums to 100 percent?
    """
    source = get_graph_root(graph)
    values = nx.get_node_attributes(graph, key)
    depths = networkx.single_source_shortest_path_length(graph, source)
    totals = pd.DataFrame(depths, index=[0]).T.groupby(by=0).apply(lambda group: sum(group.index.map(values)))
    is_100 = np.isclose(totals.values, expected, rtol=1.0e-5, atol=1.0e-8)
    if not np.all(is_100):
        for level, level_is_100 in enumerate(is_100):
            if not level_is_100:
                logging.error('%s does not sum to 100 for level %d', key, level)
        return False
    else:
        return True


@dataclasses.dataclass()
class ASCIIDisplay:
    """
    Helper class to display DAG as ASCII Art.
    """
    graph: nx.DiGraph
    CROSS: str = ' ├─'
    FINAL: str = ' └─'
    SPACE: str = '   '
    VLINE: str = ' │ '
    attrs: typing.Union[dict, bool] = dataclasses.field(default_factory=dict)
    stream: io.StringIO = dataclasses.field(default_factory=io.StringIO)
    source: str = None
    depth: int = None

    def __call__(self, *sources) -> str:
        self.stream = io.StringIO()
        self.source = get_graph_root(self.graph)
        self.depth = networkx.dag_longest_path_length(self.graph)
        for source in sources:
            self._write_node(source, "")
        return self.stream.getvalue()

    def _write_node(self, label: str, indent: str):
        if label in self.graph:
            self._write_name(label)
            children = list(self.graph.successors(label))
            for i, child in enumerate(self.graph.successors(label)):
                self._write_child_node(child, indent, i == len(children) - 1)
        else:
            label = label if label is not None else '?'
            self.stream.write(f'{label} [missing]\n')

    def _write_name(self, label):
        if self.attrs:
            level = len(nx.shortest_path(self.graph, self.source, label))
            width = 3 * (self.depth + 1) + 1 - 3 * level
            self.stream.write(f'{label:<{width}}')

            if isinstance(self.attrs, dict):
                attrs = {
                    n: (f if f is not None else '{}') for n, f in self.attrs.items()
                }
            else:
                attrs = {
                    n: '{}' for n in self.graph.nodes[label].keys()
                }

            attrs = {k: attrs[k] for k in sorted(attrs.keys())}

            for key, fmt in attrs.items():
                try:
                    val = fmt.format(self.graph.nodes[label][key])
                except KeyError:
                    val = '?'
                self.stream.write(f' {key}={val}')
            self.stream.write('\n')
        else:
            self.stream.write(f'{label}\n')

    def _write_child_node(self, label: str, indent: str, last: bool):
        self.stream.write(indent)

        if last:
            self.stream.write(self.FINAL)
            indent += self.SPACE
        else:
            self.stream.write(self.CROSS)
            indent += self.VLINE

        self._write_node(label, indent)

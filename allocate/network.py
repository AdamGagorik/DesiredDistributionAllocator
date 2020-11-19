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


def create(frame: pd.DataFrame) -> nx.DiGraph:
    """
    Transform the input data into a graph object.

    Parameters:
        frame: A dataframe with the data to build the DAG.

    Returns:
        The graph that was constructed.
    """
    raise NotImplementedError


def display(graph: nx.DiGraph, **attrs) -> str:
    """
    Display the graph using ASCII art.

    Parameters:
        graph: The DAG to display with ASCII art.
        attrs: Node attributes to display and their format strings.

    Returns:
        The graph formatted as an ASCII string.
    """
    source = get_graph_root(graph)
    return ASCIIDisplay(graph=graph, attrs=attrs)(source)


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
        network_sums_to_100_percent_at_each_level,
    ]:
        if not validator(graph):
            valid = False
    return valid


def normalize(graph: nx.DiGraph, key: str,
              levels: typing.Union[int, typing.List[int], None] = None,
              inplace: bool = True) -> nx.DiGraph:
    """
    Make it so the amounts at each level sum to 100 percent.

    Parameters:
        graph: The DAG to normalize.
        key: The name of the attribute to normalize.
        levels: The level(s) of the tree to operate on or None to normalize all levels.
        inplace: Should the operation happen in place or on a copy?

    Returns:
        The modified graph, with the value normalized.
    """
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
                graph.nodes[n][key] = d['normed']

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
                logging.debug('degree %d > 1 for node: %s', degree, n)
                valid = False

    if not valid:
        logging.debug('nodes have multiple predecessors!')

    return valid


def network_sums_to_100_percent_at_each_level(graph: nx.DiGraph, key: str) -> bool:
    """
    The fraction desired at each level sums to 100 percent?
    """
    source = get_graph_root(graph)
    values = nx.get_node_attributes(graph, key)
    depths = networkx.single_source_shortest_path_length(graph, source)
    totals = pd.DataFrame(depths, index=[0]).T.groupby(by=0).apply(lambda group: sum(group.index.map(values)))
    is_100 = np.isclose(totals.values, 100, rtol=1.0e-5, atol=1.0e-8)
    return np.all(is_100)


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

    def __call__(self, *sources) -> str:
        self.stream = io.StringIO()
        for source in sources:
            self._write_node(source, "")
        return self.stream.getvalue()

    def _write_node(self, node: str, indent: str):
        if node in self.graph:
            self._write_name(node)
            children = list(self.graph.successors(node))
            for i, child in enumerate(self.graph.successors(node)):
                self._write_child_node(child, indent, i == len(children) - 1)
        else:
            node = node if node is not None else '?'
            self.stream.write(f'{node} [missing]\n')

    def _write_name(self, node):
        if self.attrs:
            self.stream.write(f'{node}')
            if isinstance(self.attrs, dict):
                attrs = {
                    n: (f if f is not None else '{}') for n, f in self.attrs.items()
                }
            else:
                attrs = {
                    n: '{}' for n in self.graph.nodes[node].keys()
                }
            for key, fmt in attrs.items():
                try:
                    val = fmt.format(self.graph.nodes[node][key])
                except KeyError:
                    val = '?'
                self.stream.write(f' {key}={val}')
            self.stream.write('\n')
        else:
            self.stream.write(f'{node}\n')

    def _write_child_node(self, node: str, indent: str, last: bool):
        self.stream.write(indent)

        if last:
            self.stream.write(self.FINAL)
            indent += self.SPACE
        else:
            self.stream.write(self.CROSS)
            indent += self.VLINE

        self._write_node(node, indent)

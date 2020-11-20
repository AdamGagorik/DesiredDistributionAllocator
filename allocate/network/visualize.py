"""
Methods for creating a graph representation of the problem.
"""
import networkx.exception
import networkx as nx
import dataclasses
import typing
import io

import allocate.network.attributes
import allocate.network.algorithms


formats = {
    f.column: f.display for f in allocate.network.attributes.node_attrs.subset(display_only=True)
}


def text(graph: nx.DiGraph, attrs: bool = False, **kwargs) -> str:
    """
    Display the graph using ASCII art.

    Parameters:
        graph: The DAG to display with ASCII art.
        attrs: Display all node attributes for nodes?
        kwargs: Node attributes to display and their format strings.

    Returns:
        The graph formatted as an ASCII string.
    """
    source = allocate.network.algorithms.get_graph_root(graph)
    if attrs:
        return TextDisplayer(graph=graph, attrs=True)(source)
    else:
        return TextDisplayer(graph=graph, attrs=kwargs)(source)


@dataclasses.dataclass()
class TextDisplayer:
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
    depth: int = None
    source: str = None

    def __call__(self, *sources) -> str:
        self.stream = io.StringIO()
        self.depth = networkx.dag_longest_path_length(self.graph)
        for source in sources:
            self.source = source
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
            for key, fmt in self._get_node_attrs(label):
                try:
                    val = fmt.format(self.graph.nodes[label][key])
                except KeyError:
                    val = '?'
                self.stream.write(f' {key}={val}')
            self.stream.write('\n')
        else:
            self.stream.write(f'{label}\n')

    def _get_node_attrs(self, label):
        if isinstance(self.attrs, dict):
            for n, f in self.attrs.items():
                yield n, f if f is not None else '{}'
        else:
            for n in self.graph.nodes[label].keys():
                yield n, '{}'

    def _write_child_node(self, label: str, indent: str, last: bool):
        self.stream.write(indent)

        if last:
            self.stream.write(self.FINAL)
            indent += self.SPACE
        else:
            self.stream.write(self.CROSS)
            indent += self.VLINE

        self._write_node(label, indent)

"""
Create a data frame for plotting node attributes of a graph.
"""
import networkx as nx
import pandas as pd
import typing


G_ID: str = 'g_id'
NODE: str = 'node'


def create(*graphs: nx.DiGraph,
           vdims: typing.Union[typing.Iterable[str], str] = None,
           should_extract: typing.Callable = lambda g, n: True,
           add_properties: typing.Dict[str, typing.Callable] = None) -> pd.DataFrame:
    """
    Create a data frame for plotting node attributes of a graph.

    Parameters:
        *graphs: The graphs to extract data from.
        vdims: The names of the node attributes to extract.
        should_extract: A filter function taking the graph and node as input.
        add_properties: A mapping from names to functions that can extract node properties.

    Returns:
        A data frame node attributes for plotting.
    """
    if vdims is not None and isinstance(vdims, str):
        vdims = [vdims]

    def iterrows():
        for g_id, graph in enumerate(graphs):
            for node in graph:
                if should_extract(graph, node):
                    data = {
                        G_ID: g_id,
                        NODE: node,
                    }
                    if vdims:
                        for vdim in vdims:
                            data[vdim] = graph.nodes[node].get(vdim, None)
                    else:
                        for vdim in graph.nodes[node]:
                            data[vdim] = graph.nodes[node].get(vdim, None)
                    if add_properties is not None:
                        for name, method in add_properties.items():
                            data[name] = method(graph, node)
                    yield data

    return pd.DataFrame(iterrows())

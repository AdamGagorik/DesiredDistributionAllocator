"""
Create a bar plot of a single node attribute.
"""
import holoviews as hv
import networkx as nx
import typing

import allocate.network.algorithms
import allocate.plotting.node_attr_table

from allocate.plotting.node_attr_table import G_ID
from allocate.plotting.node_attr_table import NODE
from allocate.network.attributes import node_attrs

hv.extension('bokeh')


def get_plot_object(graph: nx.DiGraph, *graphs: nx.DiGraph,
                    kdims: typing.Union[typing.Iterable[str], str] = (NODE, G_ID),
                    vdims: typing.Union[typing.Iterable[str], str] = node_attrs.current_value.column,
                    **kwargs) -> hv.Element:
    """
    Create the plot object.

    Parameters:
        graph: The graph to extract data from.
        kdims: The node attributes to use for bins.
        vdims: The node attributes to use for bars.
        **kwargs: Additional parameters of node_attr_table.create method.

    Returns:
        A data frame with the data for plotting.
    """
    if isinstance(kdims, str):
        kdims = [kdims]

    if isinstance(vdims, str):
        vdims = [vdims]

    kdims = list(kdims)
    vdims = list(vdims)

    data = allocate.plotting.node_attr_table.create(graph, *graphs, vdims=vdims, **kwargs)
    plot = hv.Bars(data, kdims, [v for v in vdims if v not in kdims])
    plot = plot.opts(fontscale=2, max_width=1024, tools=['hover'], fill_color=hv.dim(kdims[0]),
                     cmap='Colorblind', fill_alpha=0.75, line_width=0, show_legend=True)
    return plot

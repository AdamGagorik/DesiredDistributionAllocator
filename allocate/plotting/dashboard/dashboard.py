"""
A dashboard composed of widgets.
"""
import panel.viewable
import panel as pn
import dataclasses

from .widgets.base import Widget


@dataclasses.dataclass()
class Dashboard(Widget):
    """The top-level widget."""
    def __setup__(self):
        """Setup the model and view for the widget."""
        pass

    def __layout__(self) -> panel.viewable.Viewable:
        """Layout the objects in the view."""
        return pn.pane.Markdown(f'{self.__class__.__name__}: NotImplemented')

    def __connect__(self):
        """Connect widgets together in the view."""
        pass

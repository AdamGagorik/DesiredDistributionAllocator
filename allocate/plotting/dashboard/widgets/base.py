"""
Base classes for widgets in a dashboard.
"""
import panel.viewable
import panel as pn
import dataclasses
import typing


LAYOUT: str = 'layout'


@dataclasses.dataclass()
class Widget:
    """
    A base class for widgets in a dashboard.
    """
    #: A reference to the parent of this widget
    parent: typing.Union[None, 'Widget'] = None
    #: References to data that is used in the view
    model: dict = dataclasses.field(default_factory=dict)
    #: The objects that are used to build up the layout
    view: dict = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        """Post initialization logic, do not override!"""
        if self.parent is not None:
            if self.parent is not self:
                if not any(v is self for v in self.parent.view.values()):
                    self.parent.view[f'{hex(id(self))}'] = self
        self.__setup__()

    def __setup__(self):
        """Setup the model and view for the widget."""
        pass

    def __layout__(self) -> panel.viewable.Viewable:
        """Layout the objects in the view."""
        return pn.pane.Markdown(f'{self.__class__.__name__}: NotImplemented')

    def __connect__(self):
        """Connect widgets together in the view."""
        pass

    def connect(self):
        """
        Call the __connect__ method for this widget, and the widget's children.
        The connect method will only be called for children that are derived from Widget.
        It really only makes sense to call this method on the top level widget before serving.
        """
        self.__connect__()
        for widget in self.view.values():
            if isinstance(widget, Widget):
                widget.connect()

    @property
    def layout(self) -> panel.viewable.Viewable:
        """Get a reference to the layout."""
        try:
            return self.view[LAYOUT]
        except KeyError:
            self.view[LAYOUT] = self.__layout__()
            return self.view[LAYOUT]

    def serve(self):
        """Serve the layout using panel app."""
        return pn.serve(self.layout)

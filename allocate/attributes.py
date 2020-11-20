"""
The data associated with each node or column when representing the problem.
"""
import dataclasses
import typing


@dataclasses.dataclass()
class Attribute:
    # name of node attribute
    column: str
    # type of node attribute
    dtype: typing.Callable
    # default value
    value: typing.Any
    # attribute is input?
    input: bool

    def __str__(self) -> str:
        return self.column

    @classmethod
    def make(cls, **kwargs) -> 'Attribute':
        """A helper function for making a dataclass field."""
        return dataclasses.field(default_factory=lambda: cls(**kwargs))


@dataclasses.dataclass()
class Attributes:
    # The label for the node
    label: Attribute = Attribute.make(column='label', dtype=str, value='', input=True)
    # The level for the node in the tree
    level: Attribute = Attribute.make(column='level', dtype=int, value=-1, input=False)
    # The desired amount in this bucket as a fraction over its level
    desired_ratio: Attribute = Attribute.make(column='desired_ratio', dtype=float, value=1.0, input=True)
    # The current amount in this bucket
    current_value: Attribute = Attribute.make(column='current_value', dtype=float, value=1.0, input=True)
    # The current amount in this bucket as a fraction over its level
    current_ratio: Attribute = Attribute.make(column='current_ratio', dtype=float, value=1.0, input=False)
    # The amount to distribute at this source over the descendents
    update_amount: Attribute = Attribute.make(column='update_amount', dtype=float, value=1.0, input=True)

    def subset(self, *columns, input_only: bool = False, strict: bool = True) \
            -> typing.Generator[Attribute, None, None]:
        """
        Select a subset of the node attributes.
        """
        if input_only:
            fields = {
                f.name: getattr(self, f.name) for f in dataclasses.fields(self) if getattr(self, f.name).input
            }
        else:
            fields = {
                f.name: getattr(self, f.name) for f in dataclasses.fields(self)
            }

        if columns:
            for label in columns:
                try:
                    yield fields[label]
                except KeyError:
                    if strict:
                        raise ValueError(label) from None
                    else:
                        pass
        else:
            for f in fields.values():
                yield f

    def dtypes(self, *columns, **kwargs):
        """
        Get the dtypes for the node attributes.
        """
        return {f.column: f.dtype for f in self.subset(*columns, **kwargs)}

    def columns(self, *columns, input_only: bool = False, **kwargs):
        """
        Get the labels for the node attributes.
        """
        return [f.column for f in self.subset(*columns, **kwargs)]


node_attrs: Attributes = Attributes()

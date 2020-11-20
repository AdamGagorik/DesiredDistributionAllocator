"""
The data associated with each node or column when representing the problem.
"""
import dataclasses
import typing


FORMAT_VALUE: str = '[{:9,.3f}]'
FORMAT_RATIO: str = '[{:5,.3f}]'


@dataclasses.dataclass()
class Attribute:
    # name of node attribute
    column: str
    # type of node attribute
    dtype: typing.Callable
    # default value
    value: typing.Any
    # format attribute in display?
    display: typing.Union[bool, str] = False
    # attribute is input?
    input: bool = False

    def __str__(self) -> str:
        return self.column

    @classmethod
    def make(cls, *args, **kwargs) -> 'Attribute':
        """A helper function for making a dataclass field."""
        return dataclasses.field(default_factory=lambda: cls(*args, **kwargs))


@dataclasses.dataclass()
class Attributes:
    # The label for the node
    label: Attribute = Attribute.make('label', str, '', False, True)
    # The level for the node in the tree
    level: Attribute = Attribute.make('level', int, -1, '[{:}]', False)
    # The current amount in this bucket
    current_value: Attribute = Attribute.make('current_value', float, 1.0, FORMAT_VALUE, True)
    # The desired amount in this bucket
    desired_value: Attribute = Attribute.make('desired_value', float, 0.0, FORMAT_VALUE, False)
    # The current amount in this bucket as a fraction over its level
    current_ratio: Attribute = Attribute.make('current_ratio', float, 1.0, FORMAT_RATIO, False)
    # The desired amount in this bucket as a fraction over its level
    desired_ratio: Attribute = Attribute.make('desired_ratio', float, 1.0, FORMAT_RATIO, True)
    # The amount to distribute at this source over the descendents
    update_amount: Attribute = Attribute.make('update_amount', float, 1.0, FORMAT_VALUE, True)

    # answer_value: Attribute = Attribute.make('solution_value', float, 0.0, FORMAT_VALUE, False)
    # solution_ratio: Attribute = Attribute.make('solution_ratio', float, 0.0, FORMAT_VALUE, False)

    def subset(self, *columns, input_only: bool = False, display_only: bool = False, strict: bool = True) \
            -> typing.Generator[Attribute, None, None]:
        """
        Select a subset of the node attributes.
        """
        fields = {
            f.name: getattr(self, f.name) for f in dataclasses.fields(self)
        }

        if input_only:
            fields = {
                n: f for n, f in fields.items() if f.input
            }

        if display_only:
            fields = {
                n: f for n, f in fields.items() if f.display
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

    def columns(self, *columns, **kwargs):
        """
        Get the labels for the node attributes.
        """
        return [f.column for f in self.subset(*columns, **kwargs)]


node_attrs: Attributes = Attributes()

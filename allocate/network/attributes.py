"""
The data associated with each node or column when representing the problem.
"""
import dataclasses
import typing


FORMAT_VALUE: str = '[{:8,.2f}]'
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
    # The optimal amount in this bucket
    optimal_value: Attribute = Attribute.make('optimal_value', float, 0.0, FORMAT_VALUE, False)
    # The solvers amount in this bucket (what we solve for)
    results_value: Attribute = Attribute.make('results_value', float, 0.0, FORMAT_VALUE, False)
    # The current amount in this bucket as a fraction over its level
    current_ratio: Attribute = Attribute.make('current_ratio', float, 1.0, FORMAT_RATIO, False)
    # The desired amount in this bucket as a fraction over its level
    optimal_ratio: Attribute = Attribute.make('optimal_ratio', float, 0.0, FORMAT_RATIO, True)
    # The solvers amount in this bucket as a fraction over its level
    results_ratio: Attribute = Attribute.make('results_ratio', float, 0.0, FORMAT_RATIO, False)
    # The product amount in this bucket as a fraction by multiplying over ancestors optimal
    # For example, given the path 1->2->3, the ratio at 3 would be ratio_1 * ratio_2 * ratio_3
    product_ratio: Attribute = Attribute.make('product_ratio', float, 0.0, FORMAT_RATIO, False)
    # The amount to distribute at this source over the descendents
    amount_to_add: Attribute = Attribute.make('amount_to_add', float, 0.0, FORMAT_VALUE, True)

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

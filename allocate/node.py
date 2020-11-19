"""
The data associated with each node or column when representing the problem.
"""
import dataclasses
import typing


@dataclasses.dataclass()
class NodeColumns:
    """
    The columns in a table representation.
    """
    label: str = 'label'
    level: str = 'level'
    desired_ratio: str = 'desired_ratio'
    current_value: str = 'current_value'
    current_ratio: str = 'current_ratio'
    update_amount: str = 'update_amount'

    @classmethod
    def values(cls, *columns, strict: bool = False):
        """
        A list of column types.
        """
        for f in dataclasses.fields(cls):
            if columns:
                if f.name in columns:
                    yield f.default
                else:
                    if strict:
                        raise ValueError(f'unknown column: {f.name}')
            else:
                yield f.default


@dataclasses.dataclass()
class NodeColumnTypes:
    """
    The columns in a table representation.
    """
    label: typing.Callable = str
    level: typing.Callable = int
    desired_ratio: typing.Callable = float
    current_value: typing.Callable = float
    current_ratio: typing.Callable = float
    update_amount: typing.Callable = float

    @classmethod
    def dtypes(cls, *columns, strict: bool = False):
        """
        A mapping from column names to types.
        """
        for f in dataclasses.fields(cls):
            if columns:
                if f.name in columns:
                    yield f.name, f.default
                else:
                    if strict:
                        raise ValueError(f'unknown column: {f.name}')
            else:
                yield f.name, f.default


@dataclasses.dataclass()
class NodeData:
    """
    The properties in a graph representation.
    """
    label: str                  # The label for the node
    level: int = -1             # The level for the node in the tree
    desired_ratio: float = 1.0  # The desired amount in this bucket as a fraction over its level
    current_value: float = 0.0  # The current amount in this bucket
    current_ratio: float = 0.0  # The current amount in this bucket as a fraction over its level
    update_amount: int = 0      # The amount to distribute at this source over the descendents

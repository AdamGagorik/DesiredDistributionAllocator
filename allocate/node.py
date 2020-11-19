"""
The data associated with each node or column when representing the problem.
"""
import dataclasses


@dataclasses.dataclass()
class COLUMNS:
    """
    The columns in a table representation.
    """
    label: str = 'label'
    level: str = 'level'
    desired_ratio: str = 'desired_ratio'
    current_value: str = 'current_value'
    current_ratio: str = 'current_ratio'
    update_amount: str = 'update_amount'


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

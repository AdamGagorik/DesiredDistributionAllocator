"""
The data associated with each node in the graph representation.
"""
import dataclasses


@dataclasses.dataclass()
class NodeData:
    """
    The data associated with each node in the graph representation.
    """
    label: str                  # The label for the node
    level: int = -1             # The level for the node in the tree
    desired_ratio: float = 1.0  # The desired amount in this bucket as a fraction over its level
    current_value: float = 0.0  # The current amount in this bucket
    current_ratio: float = 0.0  # The current amount in this bucket as a fraction over its level
    update_amount: int = 0      # The amount to distribute at this source over the descendents

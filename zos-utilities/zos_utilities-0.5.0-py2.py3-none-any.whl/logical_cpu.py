import dataclasses


@dataclasses.dataclass
class Logical_CPU:
    """
    Represents a logical CPU on an IBM Z CPC
    """

    core_id: str = None
    online: bool = None
    type: str = None
    lowid: str = None
    highid: str = None
    polarity: str = None
    parked: bool = None
    subclassmask: str = None
    core_1_state: str = None
    core_2_state: str = None

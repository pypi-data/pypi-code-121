import dataclasses
from datetime import datetime


@dataclasses.dataclass
class CPC():
    """
    Represents an IBM Z CPC, aka CEC
    """

    name: str = None
    status: str = None

    machine_model: str = None
    machine_type: str = None
    physical_general_processors: int = None
    physical_ziips: int = None
    physical_zaaps: int = None
    physical_ifls: int = None
    physical_icfs: int = None

    lpars: dict = dataclasses.field(default_factory=dict)

    start_data_gathering: datetime = None
    finish_data_gathering: datetime = None
    last_updated: datetime = None

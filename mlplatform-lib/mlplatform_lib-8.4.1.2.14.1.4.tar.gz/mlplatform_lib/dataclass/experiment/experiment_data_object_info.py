from dataclasses import dataclass, field


@dataclass
class ExperimentDataObjectInfo:
    key: str
    do_id: int = field(init=True, default=None)
    do_name: str = field(init=True, default=None)

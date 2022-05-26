from dataclasses import dataclass, field
from mlplatform_lib.dataclass.model.type import ModelStatus


@dataclass
class ModelInfoDto:
    id: int = field(init=False, default=0)
    type: str
    result: str
    finished_time: str = field(init=False)
    status: ModelStatus = field(init=False)

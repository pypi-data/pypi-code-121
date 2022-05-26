from dataclasses import dataclass
from mlplatform_lib.dataclass.model import ModelDto


@dataclass
class ModelPredefinedaiDto(ModelDto):
    algorithm: str
    metric: str
    metric_result: str

from dataclasses import dataclass
from mlplatform_lib.dataclass.model import ModelDto


@dataclass
class ModelAutomlDto(ModelDto):
    algorithm: str
    metric: str
    metric_result: str

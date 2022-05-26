from dataclasses import dataclass, field
from mlplatform_lib.dataclass.experiment.type import ExperimentType
from mlplatform_lib.dataclass.model.type import ModelStatus


@dataclass
class ModelDto:
    id: int = field(init=False, default=0)
    train_id: int = field(init=False)
    name: int
    experiment_type: ExperimentType = field(init=False)
    description: str
    model_path: str
    status: ModelStatus = field(init=False)

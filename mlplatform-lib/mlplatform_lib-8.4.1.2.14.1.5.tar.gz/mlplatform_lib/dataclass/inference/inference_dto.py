from dataclasses import dataclass, field
from mlplatform_lib.dataclass.experiment.type import ExperimentType


@dataclass
class InferenceDto:
    id: int = field(init=False, default=0)
    experiment_type: ExperimentType = field(init=False)
    inference_path: str

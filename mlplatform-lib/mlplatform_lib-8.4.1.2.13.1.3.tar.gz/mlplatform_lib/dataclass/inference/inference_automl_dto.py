from typing import Dict
from dataclasses import dataclass


@dataclass
class InferenceAutomlDto:
    id: int
    experiment_id: int
    workflow: Dict[str, str]
    experiment_type: str
    inference_path: str
    train_id: int
    input_do_id: int
    target_do_id: int

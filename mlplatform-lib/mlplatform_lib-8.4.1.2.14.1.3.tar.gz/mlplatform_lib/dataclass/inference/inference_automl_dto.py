from typing import Dict
from dataclasses import dataclass


@dataclass
class InferenceAutomlDto:
    id: int
    workflow: Dict[str, str]
    experiment_type: str
    inference_path: str
    input_do_id: int
    target_do_id: int

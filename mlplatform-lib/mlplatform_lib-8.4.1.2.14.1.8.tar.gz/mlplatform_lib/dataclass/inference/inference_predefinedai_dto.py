from typing import Dict, List
from dataclasses import dataclass


@dataclass
class InferencePredefinedaiDto:
    id: int
    experiment_id: int
    workflow: Dict[str, str]
    experiment_type: str
    inference_path: str
    train_id: int
    input_do_id: int
    target_do_id: int
    args: List[Dict[str, str]]
    envs: List[Dict[str, str]]

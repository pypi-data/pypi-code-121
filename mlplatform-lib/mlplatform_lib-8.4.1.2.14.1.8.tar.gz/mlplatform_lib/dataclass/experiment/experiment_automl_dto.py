from dataclasses import dataclass


@dataclass
class ExperimentAutomlDto:
    id: int
    authentication_id: int
    experiment_type: str
    name: str
    namespace: str
    pvc_name: str
    pvc_size: str
    created_on: str
    description: str
    do_id: int
    target_column: str
    task_type: str
    metric: str
    time_column: str
    group_columns: str

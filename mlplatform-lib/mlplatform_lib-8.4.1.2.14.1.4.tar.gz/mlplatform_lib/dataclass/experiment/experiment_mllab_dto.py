from dataclasses import dataclass


@dataclass
class ExperimentMllabDto:
    id: int
    authentication_id: int
    experiment_type: str
    name: str
    namespace: str
    pvc_name: str
    pvc_size: str
    created_on: str
    description: str
    

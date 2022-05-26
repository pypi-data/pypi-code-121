from dataclasses import dataclass, field



@dataclass
class InferenceInfoDto:
    id: int = field(init=False, default=0)
    type: str
    result: str
    finished_time: str = field(init=False)

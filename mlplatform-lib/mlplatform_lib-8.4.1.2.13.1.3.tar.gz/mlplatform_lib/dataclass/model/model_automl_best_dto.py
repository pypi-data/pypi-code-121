from dataclasses import dataclass, field


@dataclass
class ModelAutomlBestDto:
    id: int = field(init=False, default=0)
    model_id: int
    algorithm: str

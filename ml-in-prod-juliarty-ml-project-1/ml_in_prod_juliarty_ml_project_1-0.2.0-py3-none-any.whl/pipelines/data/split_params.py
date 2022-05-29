from dataclasses import dataclass, field


@dataclass()
class SplittingParams:
    test_size: float = field(default=0.15)
    random_state: int = field(default=42)

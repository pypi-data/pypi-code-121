from dataclasses import dataclass


@dataclass
class Size:

    x: float = 1.
    y: float = 1.
    z: float = 1.

    def __post_init__(self):
        if self.x < 0 or self.y < 0 or self.z < 0:
            raise ValueError("Size can't be negative")
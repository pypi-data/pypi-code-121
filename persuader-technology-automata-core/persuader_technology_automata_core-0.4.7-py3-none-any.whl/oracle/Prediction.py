from dataclasses import dataclass
from typing import List

from core.number.BigFloat import BigFloat


@dataclass
class Prediction:
    outcome: List[str]
    percent: BigFloat
    forced: bool = False

from dataclasses import dataclass

from core.number.BigFloat import BigFloat


@dataclass
class InstantRate:
    instant: int
    rate: BigFloat

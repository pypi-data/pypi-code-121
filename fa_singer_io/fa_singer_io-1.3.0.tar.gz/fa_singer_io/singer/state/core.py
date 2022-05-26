from dataclasses import (
    dataclass,
)
from fa_purity import (
    JsonObj,
)


@dataclass(frozen=True)
class SingerState:
    value: JsonObj

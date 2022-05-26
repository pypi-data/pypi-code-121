from dataclasses import (
    dataclass,
)
from fa_purity.json.factory import (
    JsonObj,
)
from fa_singer_io.time import (
    DateTime,
)
from typing import (
    Optional,
)


@dataclass(frozen=True)
class SingerRecord:
    stream: str
    record: JsonObj
    time_extracted: Optional[DateTime]

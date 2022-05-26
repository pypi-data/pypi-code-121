from fa_singer_io.singer.record import (
    SingerRecord,
)
from fa_singer_io.singer.schema import (
    SingerSchema,
)
from fa_singer_io.singer.state import (
    SingerState,
)
from typing import (
    Union,
)

SingerMessage = Union[SingerRecord, SingerSchema, SingerState]


__all__ = [
    "SingerRecord",
    "SingerSchema",
    "SingerState",
]

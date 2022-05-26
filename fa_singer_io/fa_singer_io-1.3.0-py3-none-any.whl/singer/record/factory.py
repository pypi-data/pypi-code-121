from .core import (
    SingerRecord,
)
from fa_purity import (
    Cmd,
    JsonObj,
)
from fa_singer_io.time import (
    DateTime,
)


def new_record_auto_time(stream: str, record: JsonObj) -> Cmd[SingerRecord]:
    return DateTime.now().map(lambda d: SingerRecord(stream, record, d))

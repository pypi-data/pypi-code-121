from __future__ import (
    annotations,
)

from dataclasses import (
    dataclass,
)
from datetime import (
    datetime,
)
from fa_purity.cmd import (
    Cmd,
)
from pyrfc3339 import (
    generate,
    parse as parse_rfc3339,
)
import pytz


@dataclass(frozen=True)
class _DateTime:
    _date: datetime


@dataclass(frozen=True)
class DateTime(_DateTime):
    def __init__(self, obj: _DateTime) -> None:
        _date = datetime(
            obj._date.year,
            obj._date.month,
            obj._date.day,
            obj._date.hour,
            obj._date.minute,
            obj._date.second,
            0,
            obj._date.tzinfo,
        )
        super().__init__(_date)

    @staticmethod
    def now() -> Cmd[DateTime]:
        return Cmd.from_cmd(
            lambda: DateTime(_DateTime(datetime.now(pytz.utc)))
        )

    @staticmethod
    def parse(raw: str) -> DateTime:
        draft = _DateTime(parse_rfc3339(raw))
        return DateTime(draft)

    def to_utc_str(self) -> str:
        return generate(self._date)

    def to_str(self) -> str:
        return generate(self._date, utc=False)

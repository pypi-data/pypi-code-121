from typing import NamedTuple


class StatuteLabel(NamedTuple):
    category: str
    identifier: str


class IndeterminateStatute(NamedTuple):
    text: str

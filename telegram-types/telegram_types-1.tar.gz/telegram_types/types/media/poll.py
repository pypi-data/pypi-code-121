from typing import List, Optional
from enum import auto

from telegram_types.utils import AutoName
from telegram_types.base import Base


class PollType(str, AutoName):
    regular = auto()
    quiz = auto()
    group = auto()
    supergroup = auto()
    channel = auto()


class PollOption(Base):
    text: str
    voter_count: int
    data: str


class Poll(Base):
    id: str
    question: str
    options: List[PollOption]
    total_voter_count: int
    is_closed: bool
    is_anonymous: Optional[bool]
    type: Optional[PollType]
    allows_multiple_answers: Optional[bool]
    chosen_option: Optional[int]

from typing import Optional, List
from enum import auto

from telegram_types.utils import AutoName
from telegram_types.types import Restriction, ChatPhoto
from telegram_types.base import Base


class Status(str, AutoName):
    online = auto()
    offline = auto()
    recently = auto()
    within_week = auto()
    within_month = auto()
    long_time_ago = auto()


class User(Base):
    id: int
    is_self: Optional[bool]
    is_contact: Optional[bool]
    is_mutual_contact: Optional[bool]
    is_deleted: Optional[bool]
    is_bot: Optional[bool]
    is_verified: Optional[bool]
    is_restricted: Optional[bool]
    is_scam: Optional[bool]
    is_fake: Optional[bool]
    is_support: Optional[bool]
    first_name: Optional[str]
    last_name: Optional[str]
    status: Optional[Status]
    last_online_date: Optional[int]
    next_offline_date: Optional[int]
    username: Optional[str]
    language_code: Optional[str]
    dc_id: Optional[int]
    phone_number: Optional[str]
    photo: Optional[ChatPhoto]
    restrictions: Optional[List[Restriction]]

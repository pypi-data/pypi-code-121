from typing import Optional

from telegram_types.base import Base


class Voice(Base):
    owner_id: int
    file_id: str
    file_unique_id: str
    duration: int
    waveform: Optional[str]
    mime_type: Optional[str]
    file_size: Optional[int]
    date: Optional[int]

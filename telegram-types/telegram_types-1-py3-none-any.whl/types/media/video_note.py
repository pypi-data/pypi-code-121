from typing import Optional, List

from .thumbnail import Thumbnail
from telegram_types.base import Base


class VideoNote(Base):
    owner_id: int
    file_id: str
    file_unique_id: str
    length: int
    duration: int
    mime_type: Optional[str]
    file_size: Optional[int]
    date: Optional[int]
    thumbs: Optional[List[Thumbnail]]

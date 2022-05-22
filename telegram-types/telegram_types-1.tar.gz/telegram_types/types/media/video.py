from typing import Optional, List

from .thumbnail import Thumbnail
from telegram_types.base import Base


class Video(Base):
    owner_id: int
    file_id: str
    file_unique_id: str
    width: int
    height: int
    duration: int
    file_name: Optional[str]
    mime_type: Optional[str]
    file_size: Optional[int]
    supports_streaming: Optional[bool]
    ttl_seconds: Optional[int]
    date: Optional[int]
    thumbs: Optional[List[Thumbnail]]

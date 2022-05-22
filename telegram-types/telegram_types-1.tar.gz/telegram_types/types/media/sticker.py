from typing import List, Optional

from .thumbnail import Thumbnail
from telegram_types.base import Base


class Sticker(Base):
    owner_id: int
    file_id: str
    file_unique_id: str
    width: int
    height: int
    is_animated: bool
    is_video: bool
    file_name: Optional[str]
    mime_type: Optional[str]
    file_size: Optional[int]
    date: Optional[int]
    emoji: Optional[str]
    set_name: Optional[str]
    thumbs: Optional[List[Thumbnail]]

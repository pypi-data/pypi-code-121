from typing import List, Optional

from .thumbnail import Thumbnail
from telegram_types.base import Base


class Photo(Base):
    owner_id: int
    file_id: str
    file_unique_id: str
    width: int
    height: int
    file_size: int
    date: int
    ttl_seconds: Optional[int]
    thumbs: Optional[List[Thumbnail]]

from typing import List, Optional

from .thumbnail import Thumbnail
from telegram_types.base import Base


class Document(Base):
    owner_id: int
    file_id: str
    file_unique_id: str
    file_name: Optional[str]
    mime_type: Optional[str]
    file_size: Optional[int]
    date: Optional[int]
    thumbs: Optional[List[Thumbnail]]

from typing import Optional

from . import Audio, Document, Photo, Animation, Video
from telegram_types.base import Base


class WebPage(Base):
    id: str
    url: str
    display_url: str
    type: Optional[str]
    site_name: Optional[str]
    title: Optional[str]
    description: Optional[str]
    audio: Optional[Audio]
    document: Optional[Document]
    Photo: Optional[Photo]
    animation: Optional[Animation]
    video: Optional[Video]
    embed_url: Optional[str]
    embed_type: Optional[str]
    embed_width: Optional[int]
    embed_height: Optional[int]
    duration: Optional[int]
    author: Optional[str]

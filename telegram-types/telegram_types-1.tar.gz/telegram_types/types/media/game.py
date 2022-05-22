from typing import Optional

from . import Photo, Animation
from telegram_types.base import Base


class Game(Base):
    id: int
    title: str
    short_name: str
    description: str
    photo: Photo
    thumbs: Optional[Animation]

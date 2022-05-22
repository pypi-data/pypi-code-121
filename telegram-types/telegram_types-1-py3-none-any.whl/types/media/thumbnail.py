from telegram_types.base import Base


class Thumbnail(Base):
    owner_id: int
    file_id: str
    file_unique_id: str
    width: int
    height: int
    file_size: int

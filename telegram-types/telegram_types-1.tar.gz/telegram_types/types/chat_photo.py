from telegram_types.base import Base


class ChatPhoto(Base):
    owner_id: int

    small_file_id: str
    small_photo_unique_id: str
    big_file_id: str
    big_photo_unique_id: str

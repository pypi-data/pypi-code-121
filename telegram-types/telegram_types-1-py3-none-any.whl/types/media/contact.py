from typing import Optional

from telegram_types.base import Base


class Contact(Base):
    phone_number: str
    first_name: str
    last_name: Optional[str]
    user_id: Optional[int]
    vcard: Optional[str]

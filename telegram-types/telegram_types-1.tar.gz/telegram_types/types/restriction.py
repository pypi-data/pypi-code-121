from telegram_types.base import Base


class Restriction(Base):
    platform: str
    reason: str
    text: str

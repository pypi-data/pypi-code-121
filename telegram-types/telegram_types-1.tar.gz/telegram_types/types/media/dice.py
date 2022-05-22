from telegram_types.base import Base


class Dice(Base):
    emoji: str
    value: int

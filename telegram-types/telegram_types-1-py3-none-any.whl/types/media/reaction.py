from telegram_types.base import Base


class Reaction(Base):
    emoji: str
    count: int
    chosen: bool

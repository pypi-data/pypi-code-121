from enum import Enum


class UserType(str, Enum):
    """Enum of UserTypes that symflow can manage.
    Note: Queuer has an additional UserType.SYSTEM that is not reflected here because system users
    should not be surfaced to symflow.
    """

    NORMAL = "normal"
    BOT = "bot"

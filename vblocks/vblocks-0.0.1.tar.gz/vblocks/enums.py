from enum import Enum


class StyleType(Enum):
    PRIMARY = "primary"
    DANGER = "danger"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class TextType(Enum):
    MARKDOWN = "mrkdwn"
    PLAINTEXT = "plain_text"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class TriggerActions(Enum):
    ONENTERPRESSED = "on_enter_pressed"
    ONCHARACTERENTERED = "on_character_entered"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class Include(Enum):
    IM = "im"
    MPIM = "mpim"
    PRIVATE = "private"
    PUBLIC = "public"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

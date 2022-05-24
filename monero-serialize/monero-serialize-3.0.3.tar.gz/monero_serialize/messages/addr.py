from ..core.base_types import UInt32
from ..core.message_types import MessageType
from .base import ECPublicKey


class AccountPublicAddress(MessageType):
    __slots__ = ("m_spend_public_key", "m_view_public_key")

    @staticmethod
    def f_specs():
        return (("m_spend_public_key", ECPublicKey), ("m_view_public_key", ECPublicKey))


class SubaddressIndex(MessageType):
    __slots__ = ("major", "minor")

    @staticmethod
    def f_specs():
        return (("major", UInt32), ("minor", UInt32))

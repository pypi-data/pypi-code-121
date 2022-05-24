from apps.monero.xmr.serialize.message_types import MessageType
from apps.monero.xmr.serialize_messages.base import ECKey
from apps.monero.xmr.serialize_messages.ct_keys import Key64


class BoroSig(MessageType):
    __slots__ = ("s0", "s1", "ee")

    @staticmethod
    def f_specs():
        return (("s0", Key64), ("s1", Key64), ("ee", ECKey))


class RangeSig(MessageType):
    __slots__ = ("asig", "Ci")

    @staticmethod
    def f_specs():
        return (("asig", BoroSig), ("Ci", Key64))

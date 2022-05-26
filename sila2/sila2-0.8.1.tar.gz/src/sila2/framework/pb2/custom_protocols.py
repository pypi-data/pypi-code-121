import sys
from typing import List

from sila2.framework.pb2 import SiLAFramework_pb2
from sila2.framework.pb2.SiLAFramework_pb2 import String

if sys.version_info < (3, 8):
    from typing_extensions import Protocol
else:
    from typing import Protocol


class AffectedCallsMessage(Protocol):
    AffectedCalls: List[String]

    def __init__(self, AffectedCalls: List[String]):
        self.AffectedCalls = AffectedCalls


class FeatureProtobufModule(Protocol):
    SiLAFramework__pb2: SiLAFramework_pb2

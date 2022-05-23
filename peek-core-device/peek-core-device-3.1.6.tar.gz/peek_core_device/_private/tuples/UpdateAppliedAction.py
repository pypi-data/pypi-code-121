from typing import Optional

from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType
from vortex.TupleAction import TupleActionABC

from peek_core_device._private.PluginNames import deviceTuplePrefix


@addTupleType
class UpdateAppliedAction(TupleActionABC):
    __tupleType__ = deviceTuplePrefix + "UpdateAppliedAction"

    deviceId: str = TupleField()
    appVersion: Optional[str] = TupleField()
    updateVersion: Optional[str] = TupleField()
    error: Optional[str] = TupleField()

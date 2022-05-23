from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType
from vortex.TupleAction import TupleActionABC

from peek_core_device._private.PluginNames import deviceTuplePrefix


@addTupleType
class DeviceBackgroundStateTupleAction(TupleActionABC):
    __tupleType__ = deviceTuplePrefix + "DeviceBackgroundStateTupleAction"

    deviceId: str = TupleField()
    deviceBackgrounded: bool = TupleField()

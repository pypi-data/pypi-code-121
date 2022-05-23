from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType
from vortex.TupleAction import TupleActionABC

from peek_core_device._private.PluginNames import deviceTuplePrefix
from peek_core_device.tuples.DeviceInfoTuple import DeviceInfoTuple


@addTupleType
class UpdateDeviceOnlineAction(TupleActionABC):
    __tupleType__ = deviceTuplePrefix + "UpdateDeviceOnlineAction"

    DEVICE_OFFLINE = DeviceInfoTuple.DEVICE_OFFLINE
    DEVICE_ONLINE = DeviceInfoTuple.DEVICE_ONLINE
    DEVICE_BACKGROUND = DeviceInfoTuple.DEVICE_BACKGROUND

    deviceId: str = TupleField()
    deviceStatus: int = TupleField()

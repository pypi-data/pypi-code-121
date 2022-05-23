from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_core_device._private.PluginNames import deviceTuplePrefix
from peek_core_device.tuples.DeviceInfoTuple import DeviceInfoTuple


@addTupleType
class DeviceStatusTuple(Tuple):
    __tupleType__ = deviceTuplePrefix + "DeviceStatusTuple"

    DEVICE_OFFLINE = DeviceInfoTuple.DEVICE_OFFLINE
    DEVICE_ONLINE = DeviceInfoTuple.DEVICE_ONLINE
    DEVICE_BACKGROUND = DeviceInfoTuple.DEVICE_BACKGROUND

    deviceId: str = TupleField()
    deviceToken: str = TupleField()
    deviceStatus: int = TupleField()

    @property
    def deviceOnline(self) -> bool:
        return bool(
            self.deviceStatus & self.DEVICE_ONLINE and not
            self.deviceStatus & self.DEVICE_BACKGROUND
        )

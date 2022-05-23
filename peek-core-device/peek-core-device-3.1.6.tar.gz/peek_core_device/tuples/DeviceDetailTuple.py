from datetime import datetime

from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

from peek_core_device._private.PluginNames import deviceTuplePrefix
from peek_core_device.tuples.DeviceInfoTuple import DeviceInfoTuple


@addTupleType
class DeviceDetailTuple(Tuple):
    __tupleType__ = deviceTuplePrefix + "DeviceDetailTuple"

    DEVICE_OFFLINE = DeviceInfoTuple.DEVICE_OFFLINE
    DEVICE_ONLINE = DeviceInfoTuple.DEVICE_ONLINE
    DEVICE_BACKGROUND = DeviceInfoTuple.DEVICE_BACKGROUND

    deviceToken: str = TupleField()
    deviceType: str = TupleField()
    description: str = TupleField()
    lastOnline: str = TupleField()
    deviceStatus: int = TupleField()

    def _formatDatetime(self, dt: datetime):
        return dt.strftime("%H:%M, %a, %d %b %Y")

    @property
    def deviceStatusDisplayText(self):
        if self.deviceStatus == DeviceInfoTuple.DEVICE_ONLINE:
            return "Online, App Visible"
        if self.deviceStatus == DeviceInfoTuple.DEVICE_BACKGROUND:
            return "Online, App Backgrounded"
        if self.lastOnline:
            return self._formatDatetime(self.lastOnline)
        return "Never Connected"

    @property
    def lastOnlineDisplayText(self):
        return self._formatDatetime(self.lastOnline)

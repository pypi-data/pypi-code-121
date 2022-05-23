import datetime as datetime

from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType
from vortex.TupleAction import TupleActionABC

from peek_core_device._private.PluginNames import deviceTuplePrefix


@addTupleType
class UpdateDeviceGpsLocationTupleAction(TupleActionABC):
    __tupleType__ = deviceTuplePrefix + "GpsLocationUpdateTupleAction"
    ACCURACY_COARSE = 1
    ACCURACY_FINE = 2

    latitude: float = TupleField()
    longitude: float = TupleField()
    updateType: int = TupleField()
    datetime: datetime = TupleField()
    deviceToken: str = TupleField()

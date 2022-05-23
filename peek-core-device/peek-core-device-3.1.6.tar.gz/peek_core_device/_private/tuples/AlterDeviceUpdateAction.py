from typing import Optional

from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType
from vortex.TupleAction import TupleActionABC

from peek_core_device._private.PluginNames import deviceTuplePrefix


# I'm using the word Alter here, because UpdateUpdate is confusing.
@addTupleType
class AlterDeviceUpdateAction(TupleActionABC):
    """Alter Device Update Tuple

    This action tuple applies changes to the Update from the admin UI.

    """

    __tupleType__ = deviceTuplePrefix + "AlterDeviceUpdateAction"

    #:  the ID of the DeviceUpdateTuple
    updateId: int = TupleField()

    #: Set the enabled property of the update
    isEnabled: Optional[bool] = TupleField()

    #: Delete the update from the database
    remove: bool = TupleField(False)

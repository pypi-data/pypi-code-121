from typing import Dict

from peek_abstract_chunked_index.private.tuples.ACIUpdateDateTupleABC import (
    ACIUpdateDateTupleABC,
)
from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from vortex.Tuple import addTupleType, TupleField, Tuple

#: This the type of the data that we get when the clients observe new locationIndexs.
DeviceLocationIndexT = Dict[str, str]


@addTupleType
class LocationIndexUpdateDateTuple(Tuple, ACIUpdateDateTupleABC):
    __tupleType__ = diagramTuplePrefix + "LocationIndexUpdateDateTuple"

    # Improve performance of the JSON serialisation
    __rawJonableFields__ = ("initialLoadComplete", "updateDateByChunkKey")

    initialLoadComplete: bool = TupleField()
    updateDateByChunkKey: DeviceLocationIndexT = TupleField({})

    @property
    def ckiUpdateDateByChunkKey(self):
        return self.updateDateByChunkKey

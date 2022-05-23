from datetime import datetime

from vortex.Tuple import addTupleType, TupleField, Tuple

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix


@addTupleType
class EncodedGridTuple(Tuple):
    """Encoded Grid Tuple

    This tuple stores a pre-encoded version of a GridTuple

    """

    __tupleType__ = diagramTuplePrefix + "EncodedGridTuple"

    gridKey: str = TupleField()

    # A GridTuple, already encoded and ready for storage in the clients cache
    encodedGridTuple: str = TupleField()

    lastUpdate: datetime = TupleField()

    @property
    def ckiChunkKey(self):
        return self.gridKey

    @property
    def ckiHasEncodedData(self) -> bool:
        return bool(self.encodedGridTuple)

    @property
    def ckiLastUpdate(self):
        return self.lastUpdate

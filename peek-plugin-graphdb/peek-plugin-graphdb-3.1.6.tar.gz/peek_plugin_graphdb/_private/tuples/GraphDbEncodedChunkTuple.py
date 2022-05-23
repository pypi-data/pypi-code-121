import logging

from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix

logger = logging.getLogger(__name__)


@addTupleType
class GraphDbEncodedChunkTuple(Tuple):
    __tupleType__ = graphDbTuplePrefix + "GraphDbEncodedChunkTuple"

    modelSetKey: str = TupleField()

    chunkKey: str = TupleField()
    encodedData: bytes = TupleField()
    encodedHash: str = TupleField()
    lastUpdate: str = TupleField()

    @property
    def ckiChunkKey(self):
        return self.chunkKey

    @property
    def ckiHasEncodedData(self) -> bool:
        return bool(self.encodedData)

    @property
    def ckiLastUpdate(self):
        return self.lastUpdate

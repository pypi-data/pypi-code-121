from typing import Dict

from peek_plugin_graphdb.tuples.GraphDbImportEdgeTuple import GraphDbImportEdgeTuple
from peek_plugin_graphdb.tuples.GraphDbLinkedVertex import GraphDbLinkedVertex


class GraphDbLinkedEdge:
    """Graph DB Linked Edge

    This tuple is a connection between two vertices.

    """

    __slots__ = ("_k", "_s", "_d", "_sd", "_p")

    DIR_UNKNOWN = GraphDbImportEdgeTuple.DIR_UNKNOWN
    DIR_SRC_IS_UPSTREAM = GraphDbImportEdgeTuple.DIR_SRC_IS_UPSTREAM
    DIR_SRC_IS_DOWNSTREAM = GraphDbImportEdgeTuple.DIR_SRC_IS_DOWNSTREAM
    DIR_SRC_IS_BOTH = GraphDbImportEdgeTuple.DIR_SRC_IS_BOTH

    @property
    def key(self) -> str:
        return self._k

    @property
    def srcVertex(self) -> GraphDbLinkedVertex:
        return self._s

    @property
    def dstVertex(self) -> GraphDbLinkedVertex:
        return self._d

    @property
    def srcDirection(self) -> int:
        return self._sd

    @property
    def props(self) -> Dict[str, str]:
        if self._p is None:
            self._p = {}
        return self._p

    def getOtherVertex(self, vertexKey: str) -> GraphDbLinkedVertex:
        if self.srcVertex.key == vertexKey:
            return self.dstVertex
        return self.srcVertex

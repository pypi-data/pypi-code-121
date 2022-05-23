from typing import Dict, Any

from vortex.Tuple import Tuple, addTupleType

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix


@addTupleType
class GraphDbImportEdgeTuple(Tuple):
    """Graph DB Edge Tuple

    This tuple represents a connection between two vertices.

    """

    __tupleType__ = graphDbTuplePrefix + "GraphDbImportEdgeTuple"
    __slots__ = ("k", "sk", "dk", "p", "sd")
    __rawJonableFields__ = ["p"]

    DIR_UNKNOWN = 0
    DIR_SRC_IS_UPSTREAM = 1
    DIR_SRC_IS_DOWNSTREAM = 2
    DIR_SRC_IS_BOTH = 3

    @property
    def key(self) -> str:
        return self.k

    @key.setter
    def key(self, val) -> None:
        self.k = val

    @property
    def srcVertexKey(self) -> str:
        return self.sk

    @srcVertexKey.setter
    def srcVertexKey(self, val) -> None:
        self.sk = val

    @property
    def dstVertexKey(self) -> str:
        return self.dk

    @dstVertexKey.setter
    def dstVertexKey(self, val) -> None:
        self.dk = val

    @property
    def srcDirection(self) -> int:
        return self.sd

    @srcDirection.setter
    def srcDirection(self, val) -> None:
        self.sd = val

    @property
    def props(self) -> Dict[str, str]:
        if self.p is None:
            self.p = {}
        return self.p

    @props.setter
    def props(self, val) -> None:
        self.p = val

    def __repr__(self):
        return "%s.%s.%s.%s.%s" % (self.k, self.sk, self.dk, self.sd, self.p)

    def sortSrcDstForHash(self) -> None:
        if self.srcVertexKey < self.dstVertexKey:
            return

        # Flip the source and destination so hashing is consistent.

        self.dstVertexKey, self.srcVertexKey = self.srcVertexKey, self.dstVertexKey
        if self.srcDirection == self.DIR_SRC_IS_DOWNSTREAM:
            self.srcDirection = self.DIR_SRC_IS_UPSTREAM

        elif self.srcDirection == self.DIR_SRC_IS_UPSTREAM:
            self.srcDirection = self.DIR_SRC_IS_DOWNSTREAM

    def packJsonDict(self) -> Dict[str, Any]:
        jsonDict = dict(k=self.k, sk=self.sk, dk=self.dk, p=self.p)
        if self.sd:
            jsonDict["sd"] = self.sd
        return jsonDict

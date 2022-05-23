# coding=utf-8
from __future__ import absolute_import, print_function

import base64
import copy
import itertools
import re
from collections import namedtuple

from lostc import collection as lcc

from suanpan import error, g
from suanpan.app import arguments
from suanpan.log import logger
from suanpan.objects import HasName
from suanpan.utils import functional, json

Param = namedtuple("Param", ["uuid", "name", "type"])
Port = namedtuple("Port", ["uuid", "name", "type", "subtype", "description"], defaults=[{}])

DEFAULT_DATA_SUBTYPE_ARGS_MAP = {
    "all": arguments.String,
    "number": arguments.IntOrFloat,
    "bool": arguments.Bool,
    "string": arguments.String,
    "array": arguments.Json,
    "dyadicArray": arguments.Json,
    "json": arguments.Json,
    "file": arguments.File,
    "csv": arguments.Csv,
    "npy": arguments.Npy,
    "model": arguments.Model,
    "image": arguments.Image,
    "system": arguments.String,
    # not used now
    "int": arguments.Int,
    "float": arguments.Float,
    "folder": arguments.Folder,
    "data": arguments.Data,
    "excel": arguments.Excel,
    "table": arguments.Table,
    "dataframe": arguments.Csv,
}

DEFAULT_PARAM_TYPE_ARGS_MAP = {
    "string": arguments.String,
}


class BaseNode(HasName):
    NODE_INFO_KEY = "SP_NODE_INFO"
    DEFAULT_NODE_INFO = {"info": {}, "inputs": {}, "outputs": {}, "params": {}}

    def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
        super().__init__()
        self._node = self.load()
        self._data_subtype_args_map = copy.copy(DEFAULT_DATA_SUBTYPE_ARGS_MAP)
        self._param_type_args_map = copy.copy(DEFAULT_PARAM_TYPE_ARGS_MAP)

    def __getattr__(self, key):
        value = self._getPort(key) if re.match(r"(in|out)\d+", key) else self.get(key)
        return value or self.__getattribute__(key)

    def _getPort(self, key):
        return lcc.first(
            itertools.chain(self.inputs, self.outputs), lambda i: i.uuid == key
        )

    def get(self, key, default=None):
        for _, collection in self._node.items():
            if isinstance(collection, dict):
                if key in collection:
                    return collection[key]
        return default

    @property
    def info(self):
        return self._node["info"]

    @property
    def inputs(self):
        return self._node["inputs"].values()

    @property
    def ins(self):
        return self._node["inputs"].values()

    @property
    def outputs(self):
        return self._node["outputs"].values()

    @property
    def outs(self):
        return self._node["outputs"].values()

    @property
    def params(self):
        return self._node["params"].values()

    def loadFromEnv(self):
        nodeInfoBase64 = g.nodeInfo
        logger.debug(f"{self.NODE_INFO_KEY}(Base64)='{nodeInfoBase64}'")
        nodeInfoString = base64.b64decode(nodeInfoBase64).decode()
        nodeInfo = json.loads(nodeInfoString)
        return nodeInfo

    def formatNodeInfo(self, nodeInfo):
        inputs = {
            name: Port(**port) for name, port in nodeInfo.get("inputs", {}).items()
        }
        outputs = {
            name: Port(**port) for name, port in nodeInfo.get("outputs", {}).items()
        }
        params = {
            name: Param(**param) for name, param in nodeInfo.get("params", {}).items()
        }
        return {"inputs": inputs, "outputs": outputs, "params": params}

    def defaultNodeInfo(self):
        return copy.deepcopy(self.DEFAULT_NODE_INFO)

    def _updateInfo(self, *infos):
        result = self.defaultNodeInfo()
        keys = result.keys()
        for info in infos:
            for key in keys:
                result[key].update(info.get(key, {}))
        return result

    def load(self):
        return self._updateInfo(self.formatNodeInfo(self.loadFromEnv()))

    def setDataSubtypeArgs(self, *args, **kwargs):
        self._data_subtype_args_map.update(*args, **kwargs)

    def setParamTypeArgs(self, *args, **kwargs):
        self._param_type_args_map.update(*args, **kwargs)

    def _portArg(self, port, prefix):
        n = port.uuid[len(prefix):]
        if port.type == "table":
            return arguments.Table(
                f"{prefix}putData{n}",
                table=f"{prefix}putTable{n}",
                partition=f"{prefix}putPartition{n}",
                alias=port.uuid,
            )
        if port.type == "visual":
            return arguments.Visual(port.name, alias=port.uuid)
        if port.type == "data":
            argtype = self._data_subtype_args_map.get(port.subtype)
            if not argtype:
                raise error.NodeAutoLoadUnsupportedDataSubtypeError(port.subtype)
            return argtype(port.name, alias=port.uuid)
        if port.type in self._data_subtype_args_map:
            logger.info(f"Node auto load {prefix} type: {port.type}")
            argtype = self._data_subtype_args_map.get(port.type)
            if not argtype:
                raise error.NodeAutoLoadUnsupportedDataSubtypeError(port.subtype)
            return argtype(port.name, alias=port.uuid)
        logger.warning(f"Node auto load not support {prefix} type: {port.type}")
        return None

    def _inPortArgs(self):
        inPorts = {p.uuid: p for p in self.ins}.values()
        args = (self._portArg(p, prefix="in") for p in inPorts)
        return [arg for arg in args if arg is not None]

    def _outPortArgs(self):
        outPorts = {p.uuid: p for p in self.outs}.values()
        args = (self._portArg(p, prefix="out") for p in outPorts)
        return [arg for arg in args if arg is not None]

    def _paramArg(self, param):
        argtype = self._data_subtype_args_map.get(param.type)
        if not argtype:
            raise error.NodeAutoLoadUnsupportedParamTypeError(param.type)
        return argtype(param.name)

    def _paramArgs(self):
        args = (self._paramArg(p) for p in self.params if p.name.startswith("param"))
        return [arg for arg in args if arg is not None]

    @functional.lazyproperty
    def inargs(self):
        return self._inPortArgs()

    @functional.lazyproperty
    def outargs(self):
        return self._outPortArgs()

    @functional.lazyproperty
    def paramargs(self):
        return self._paramArgs()

    def json(self):
        return {
            "info": self.info,
            "inputs": [i._asdict() for i in self.ins],
            "outputs": [i._asdict() for i in self.outs],
            "params": [i._asdict() for i in self.params],
        }

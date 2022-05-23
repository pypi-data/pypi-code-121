from vortex.handler.TupleActionProcessorProxy import TupleActionProcessorProxy

from peek_core_device._private.PluginNames import deviceActionProcessorName
from peek_core_device._private.PluginNames import deviceFilt
from peek_plugin_base.PeekVortexUtil import peekServerName


def makeTupleActionProcessorProxy():
    return TupleActionProcessorProxy(
        tupleActionProcessorName=deviceActionProcessorName,
        proxyToVortexName=peekServerName,
        additionalFilt=deviceFilt,
    )

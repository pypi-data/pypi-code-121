from vortex.handler.TupleDataObservableProxyHandler import (
    TupleDataObservableProxyHandler,
)

from peek_core_device._private.PluginNames import deviceFilt
from peek_core_device._private.PluginNames import deviceObservableName
from peek_plugin_base.PeekVortexUtil import peekServerName


def makeDeviceTupleDataObservableProxy():
    proxy = TupleDataObservableProxyHandler(
        observableName=deviceObservableName,
        proxyToVortexName=peekServerName,
        additionalFilt=deviceFilt,
    )

    return proxy

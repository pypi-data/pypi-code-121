from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_docdb_generic_menu._private.PluginNames import docDbGenericMenuFilt
from peek_plugin_docdb_generic_menu._private.PluginNames import (
    docDbGenericMenuObservableName,
)
from vortex.handler.TupleDataObservableProxyHandler import (
    TupleDataObservableProxyHandler,
)


def makeDeviceTupleDataObservableProxy():
    return TupleDataObservableProxyHandler(
        observableName=docDbGenericMenuObservableName,
        proxyToVortexName=peekServerName,
        additionalFilt=docDbGenericMenuFilt,
    )

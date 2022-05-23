from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_docdb_generic_menu._private.PluginNames import docDbGenericMenuFilt
from peek_plugin_docdb_generic_menu._private.PluginNames import (
    docDbGenericMenuActionProcessorName,
)
from vortex.handler.TupleActionProcessorProxy import TupleActionProcessorProxy


def makeTupleActionProcessorProxy():
    return TupleActionProcessorProxy(
        tupleActionProcessorName=docDbGenericMenuActionProcessorName,
        proxyToVortexName=peekServerName,
        additionalFilt=docDbGenericMenuFilt,
    )

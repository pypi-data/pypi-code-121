from peek_core_search._private.client.controller.FastKeywordController import (
    FastKeywordController,
)
from peek_core_search._private.tuples.KeywordAutoCompleteTupleAction import (
    KeywordAutoCompleteTupleAction,
)
from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_core_search._private.PluginNames import searchFilt
from peek_core_search._private.PluginNames import searchActionProcessorName
from vortex.handler.TupleActionProcessorProxy import TupleActionProcessorProxy


def makeTupleActionProcessorProxy(fastKeywordController: FastKeywordController):
    proxy = TupleActionProcessorProxy(
        tupleActionProcessorName=searchActionProcessorName,
        proxyToVortexName=peekServerName,
        additionalFilt=searchFilt,
    )

    proxy.setDelegate(KeywordAutoCompleteTupleAction.tupleType(), fastKeywordController)

    return proxy

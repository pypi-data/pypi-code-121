from vortex.handler.TupleActionProcessor import TupleActionProcessor

from peek_plugin_docdb_generic_menu._private.PluginNames import docDbGenericMenuFilt
from peek_plugin_docdb_generic_menu._private.PluginNames import (
    docDbGenericMenuActionProcessorName,
)
from .controller.MainController import MainController


def makeTupleActionProcessorHandler(mainController: MainController):
    processor = TupleActionProcessor(
        tupleActionProcessorName=docDbGenericMenuActionProcessorName,
        additionalFilt=docDbGenericMenuFilt,
        defaultDelegate=mainController,
    )
    return processor

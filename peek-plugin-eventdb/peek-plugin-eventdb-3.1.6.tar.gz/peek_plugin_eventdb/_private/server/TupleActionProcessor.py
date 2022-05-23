from vortex.handler.TupleActionProcessor import TupleActionProcessor

from peek_plugin_eventdb._private.PluginNames import eventdbFilt
from peek_plugin_eventdb._private.PluginNames import eventdbActionProcessorName
from .controller.MainController import MainController


def makeTupleActionProcessorHandler(mainController: MainController):
    processor = TupleActionProcessor(
        tupleActionProcessorName=eventdbActionProcessorName,
        additionalFilt=eventdbFilt,
        defaultDelegate=mainController,
    )
    return processor

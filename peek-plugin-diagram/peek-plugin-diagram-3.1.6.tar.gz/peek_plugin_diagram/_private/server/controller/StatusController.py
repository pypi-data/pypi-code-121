import logging

from peek_abstract_chunked_index.private.server.controller.ACIProcessorStatusControllerABC import (
    ACIProcessorStatusControllerABC,
)
from peek_plugin_diagram._private.tuples.DiagramImporterStatusTuple import (
    DiagramImporterStatusTuple,
)

logger = logging.getLogger(__name__)


class StatusController(ACIProcessorStatusControllerABC):
    NOTIFY_PERIOD = 2.0

    _StateTuple = DiagramImporterStatusTuple

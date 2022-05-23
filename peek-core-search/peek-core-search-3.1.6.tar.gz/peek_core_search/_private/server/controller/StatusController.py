import logging

from peek_abstract_chunked_index.private.server.controller.ACIProcessorStatusControllerABC import (
    ACIProcessorStatusControllerABC,
)
from peek_core_search._private.tuples.AdminStatusTuple import AdminStatusTuple

logger = logging.getLogger(__name__)


class StatusController(ACIProcessorStatusControllerABC):
    NOTIFY_PERIOD = 2.0

    _StateTuple = AdminStatusTuple

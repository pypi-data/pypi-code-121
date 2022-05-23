import logging

from peek_abstract_chunked_index.private.server.controller.ACIProcessorQueueControllerABC import (
    ACIProcessorQueueControllerABC,
    ACIProcessorQueueBlockItem,
)
from peek_abstract_chunked_index.private.server.controller.ACIProcessorStatusNotifierABC import (
    ACIProcessorStatusNotifierABC,
)
from peek_abstract_chunked_index.private.tuples.ACIProcessorQueueTupleABC import (
    ACIProcessorQueueTupleABC,
)
from peek_plugin_diagram._private.server.client_handlers.ClientGridUpdateHandler import (
    ClientGridUpdateHandler,
)
from peek_plugin_diagram._private.server.controller.StatusController import (
    StatusController,
)
from peek_plugin_diagram._private.storage.GridKeyIndex import (
    GridKeyCompilerQueue,
    GridKeyIndexCompiled,
    GridKeyIndex,
)

logger = logging.getLogger(__name__)


class _Notifier(ACIProcessorStatusNotifierABC):
    def __init__(self, adminStatusController: StatusController):
        self._adminStatusController = adminStatusController

    def setProcessorStatus(self, state: bool, queueSize: int):
        self._adminStatusController.status.gridCompilerQueueStatus = state
        self._adminStatusController.status.gridCompilerQueueSize = queueSize
        self._adminStatusController.notify()

    def addToProcessorTotal(self, delta: int):
        self._adminStatusController.status.gridCompilerProcessedTotal += delta
        self._adminStatusController.notify()

    def setProcessorError(self, error: str):
        self._adminStatusController.status.gridCompilerLastError = error
        self._adminStatusController.notify()


class GridKeyCompilerQueueController(ACIProcessorQueueControllerABC):
    QUEUE_ITEMS_PER_TASK = 5
    POLL_PERIOD_SECONDS = 0.200

    # We don't deduplicate this queue, so we can fill it up
    QUEUE_BLOCKS_MAX = 30
    QUEUE_BLOCKS_MIN = 2

    WORKER_TASK_TIMEOUT = 60.0

    _logger = logger
    _QueueDeclarative: ACIProcessorQueueTupleABC = GridKeyCompilerQueue
    _VacuumDeclaratives = (GridKeyCompilerQueue, GridKeyIndex, GridKeyIndexCompiled)

    def __init__(
        self,
        dbSessionCreator,
        statusController: StatusController,
        clientGridUpdateHandler: ClientGridUpdateHandler,
    ):
        ACIProcessorQueueControllerABC.__init__(
            self, dbSessionCreator, _Notifier(statusController)
        )

        self._clientGridUpdateHandler: ClientGridUpdateHandler = clientGridUpdateHandler

    def _sendToWorker(self, block: ACIProcessorQueueBlockItem):
        from peek_plugin_diagram._private.worker.tasks.GridCompilerTask import (
            compileGrids,
        )

        return compileGrids.delay(block.itemsEncodedPayload)

    def _processWorkerResults(self, results):
        self._clientGridUpdateHandler.sendChunks(results)

    def _dedupeQueueSql(self, lastFetchedId: int, dedupeLimit: int):
        return """
                 with sq_raw as (
                    SELECT "id", "gridKey"
                    FROM pl_diagram."GridKeyCompilerQueue"
                    WHERE id > %(id)s
                    LIMIT %(limit)s
                ), sq as (
                    SELECT min(id) as "minId", "gridKey"
                    FROM sq_raw
                    GROUP BY  "gridKey"
                    HAVING count("gridKey") > 1
                )
                DELETE
                FROM pl_diagram."GridKeyCompilerQueue"
                     USING sq sq1
                WHERE pl_diagram."GridKeyCompilerQueue"."id" != sq1."minId"
                    AND pl_diagram."GridKeyCompilerQueue"."id" > %(id)s
                    AND pl_diagram."GridKeyCompilerQueue"."gridKey" = sq1."gridKey"

            """ % {
            "id": lastFetchedId,
            "limit": dedupeLimit,
        }

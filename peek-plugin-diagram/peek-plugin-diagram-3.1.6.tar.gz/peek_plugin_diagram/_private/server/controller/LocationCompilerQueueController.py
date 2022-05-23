import logging
from typing import Callable

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
from peek_plugin_diagram._private.server.client_handlers.ClientLocationIndexUpdateHandler import (
    ClientLocationIndexUpdateHandler,
)
from peek_plugin_diagram._private.server.controller.StatusController import (
    StatusController,
)
from peek_plugin_diagram._private.storage.LocationIndex import (
    LocationIndexCompilerQueue,
    LocationIndexCompiled,
    LocationIndex,
)

logger = logging.getLogger(__name__)


class _Notifier(ACIProcessorStatusNotifierABC):
    def __init__(self, adminStatusController: StatusController):
        self._adminStatusController = adminStatusController

    def setProcessorStatus(self, state: bool, queueSize: int):
        self._adminStatusController.status.locationIndexCompilerQueueStatus = state
        self._adminStatusController.status.locationIndexCompilerQueueSize = queueSize
        self._adminStatusController.notify()

    def addToProcessorTotal(self, delta: int):
        self._adminStatusController.status.locationIndexCompilerProcessedTotal += delta
        self._adminStatusController.notify()

    def setProcessorError(self, error: str):
        self._adminStatusController.status.locationIndexCompilerLastError = error
        self._adminStatusController.notify()


class LocationCompilerQueueController(ACIProcessorQueueControllerABC):
    QUEUE_ITEMS_PER_TASK = 10
    POLL_PERIOD_SECONDS = 2.000

    QUEUE_BLOCKS_MAX = 5
    QUEUE_BLOCKS_MIN = 0

    WORKER_TASK_TIMEOUT = 60.0

    _logger = logger
    _QueueDeclarative: ACIProcessorQueueTupleABC = LocationIndexCompilerQueue
    _VacuumDeclaratives = (
        LocationIndexCompilerQueue,
        LocationIndex,
        LocationIndexCompiled,
    )

    def __init__(
        self,
        dbSessionCreator,
        statusController: StatusController,
        clientLocationUpdateHandler: ClientLocationIndexUpdateHandler,
        readyLambdaFunc: Callable,
    ):
        ACIProcessorQueueControllerABC.__init__(
            self, dbSessionCreator, _Notifier(statusController)
        )
        # Disabled
        # isProcessorEnabledCallable=readyLambdaFunc)

        self._clientLocationUpdateHandler: ClientLocationIndexUpdateHandler = (
            clientLocationUpdateHandler
        )

    def _sendToWorker(self, block: ACIProcessorQueueBlockItem):
        from peek_plugin_diagram._private.worker.tasks.LocationIndexCompilerTask import (
            compileLocationIndex,
        )

        return compileLocationIndex.delay(block.itemsEncodedPayload)

    def _processWorkerResults(self, results):
        self._clientLocationUpdateHandler.sendChunks(results)

    def _dedupeQueueSql(self, lastFetchedId: int, dedupeLimit: int):
        return """
                 with sq_raw as (
                    SELECT "id", "indexBucket", "modelSetId"
                    FROM pl_diagram."LocationIndexCompilerQueue"
                    WHERE id > %(id)s
                    LIMIT %(limit)s
                ), sq as (
                    SELECT min(id) as "minId", "indexBucket", "modelSetId"
                    FROM sq_raw
                    GROUP BY  "indexBucket", "modelSetId"
                    HAVING count("indexBucket") > 1
                )
                DELETE
                FROM pl_diagram."LocationIndexCompilerQueue"
                     USING sq sq1
                WHERE pl_diagram."LocationIndexCompilerQueue"."id" != sq1."minId"
                    AND pl_diagram."LocationIndexCompilerQueue"."id" > %(id)s
                    AND pl_diagram."LocationIndexCompilerQueue"."indexBucket" = sq1."indexBucket"
                    AND pl_diagram."LocationIndexCompilerQueue"."modelSetId" = sq1."modelSetId"

            """ % {
            "id": lastFetchedId,
            "limit": dedupeLimit,
        }

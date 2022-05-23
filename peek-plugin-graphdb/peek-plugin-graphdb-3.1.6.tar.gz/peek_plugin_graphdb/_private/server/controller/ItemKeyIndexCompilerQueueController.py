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
from peek_plugin_graphdb._private.server.client_handlers.ItemKeyIndexChunkUpdateHandler import (
    ItemKeyIndexChunkUpdateHandler,
)
from peek_plugin_graphdb._private.server.controller.StatusController import (
    StatusController,
)
from peek_plugin_graphdb._private.storage.ItemKeyIndex import ItemKeyIndex
from peek_plugin_graphdb._private.storage.ItemKeyIndexCompilerQueue import (
    ItemKeyIndexCompilerQueue,
)
from peek_plugin_graphdb._private.storage.ItemKeyIndexEncodedChunk import (
    ItemKeyIndexEncodedChunk,
)

logger = logging.getLogger(__name__)


class _Notifier(ACIProcessorStatusNotifierABC):
    def __init__(self, adminStatusController: StatusController):
        self._adminStatusController = adminStatusController

    def setProcessorStatus(self, state: bool, queueSize: int):
        self._adminStatusController.status.itemKeyIndexCompilerQueueStatus = state
        self._adminStatusController.status.itemKeyIndexCompilerQueueSize = queueSize
        self._adminStatusController.notify()

    def addToProcessorTotal(self, delta: int):
        self._adminStatusController.status.itemKeyIndexCompilerQueueProcessedTotal += (
            delta
        )
        self._adminStatusController.notify()

    def setProcessorError(self, error: str):
        self._adminStatusController.status.itemKeyIndexCompilerQueueLastError = error
        self._adminStatusController.notify()


class ItemKeyIndexCompilerQueueController(ACIProcessorQueueControllerABC):
    QUEUE_ITEMS_PER_TASK = 10
    POLL_PERIOD_SECONDS = 1.000

    QUEUE_BLOCKS_MAX = 20
    QUEUE_BLOCKS_MIN = 4

    WORKER_TASK_TIMEOUT = 60.0

    _logger = logger
    _QueueDeclarative: ACIProcessorQueueTupleABC = ItemKeyIndexCompilerQueue
    _VacuumDeclaratives = (
        ItemKeyIndexCompilerQueue,
        ItemKeyIndex,
        ItemKeyIndexEncodedChunk,
    )

    def __init__(
        self,
        dbSessionCreator,
        statusController: StatusController,
        clientUpdateHandler: ItemKeyIndexChunkUpdateHandler,
    ):
        ACIProcessorQueueControllerABC.__init__(
            self, dbSessionCreator, _Notifier(statusController)
        )

        self._clientUpdateHandler: ItemKeyIndexChunkUpdateHandler = clientUpdateHandler

    def _sendToWorker(self, block: ACIProcessorQueueBlockItem):
        from peek_plugin_graphdb._private.worker.tasks.ItemKeyIndexCompiler import (
            compileItemKeyIndexChunk,
        )

        return compileItemKeyIndexChunk.delay(block.itemsEncodedPayload)

    def _processWorkerResults(self, results):
        self._clientUpdateHandler.sendChunks(results)

    def _dedupeQueueSql(self, lastFetchedId: int, dedupeLimit: int):
        return """
                 with sq_raw as (
                    SELECT "id", "chunkKey"
                    FROM pl_graphdb."ItemKeyIndexCompilerQueue"
                    WHERE id > %(id)s
                    LIMIT %(limit)s
                ), sq as (
                    SELECT min(id) as "minId", "chunkKey"
                    FROM sq_raw
                    GROUP BY  "chunkKey"
                    HAVING count("chunkKey") > 1
                )
                DELETE
                FROM pl_graphdb."ItemKeyIndexCompilerQueue"
                     USING sq sq1
                WHERE pl_graphdb."ItemKeyIndexCompilerQueue"."id" != sq1."minId"
                    AND pl_graphdb."ItemKeyIndexCompilerQueue"."id" > %(id)s
                    AND pl_graphdb."ItemKeyIndexCompilerQueue"."chunkKey" = sq1."chunkKey"

            """ % {
            "id": lastFetchedId,
            "limit": dedupeLimit,
        }

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
from peek_core_search._private.server.client_handlers.ClientSearchObjectChunkUpdateHandler import (
    ClientSearchObjectChunkUpdateHandler,
)
from peek_core_search._private.server.controller.StatusController import (
    StatusController,
)
from peek_core_search._private.storage.EncodedSearchObjectChunk import (
    EncodedSearchObjectChunk,
)
from peek_core_search._private.storage.SearchObject import SearchObject
from peek_core_search._private.storage.SearchObjectCompilerQueue import (
    SearchObjectCompilerQueue,
)

logger = logging.getLogger(__name__)


class _Notifier(ACIProcessorStatusNotifierABC):
    def __init__(self, adminStatusController: StatusController):
        self._adminStatusController = adminStatusController

    def setProcessorStatus(self, state: bool, queueSize: int):
        self._adminStatusController.status.searchObjectCompilerQueueStatus = state
        self._adminStatusController.status.searchObjectCompilerQueueSize = queueSize
        self._adminStatusController.notify()

    def addToProcessorTotal(self, delta: int):
        self._adminStatusController.status.searchObjectCompilerQueueProcessedTotal += (
            delta
        )
        self._adminStatusController.notify()

    def setProcessorError(self, error: str):
        self._adminStatusController.status.searchObjectCompilerQueueLastError = error
        self._adminStatusController.notify()


class SearchObjectChunkCompilerQueueController(ACIProcessorQueueControllerABC):
    QUEUE_ITEMS_PER_TASK = 10
    POLL_PERIOD_SECONDS = 1.000

    QUEUE_BLOCKS_MAX = 20
    QUEUE_BLOCKS_MIN = 4

    WORKER_TASK_TIMEOUT = 60.0

    _logger = logger
    _QueueDeclarative: ACIProcessorQueueTupleABC = SearchObjectCompilerQueue
    _VacuumDeclaratives = (
        SearchObjectCompilerQueue,
        SearchObject,
        EncodedSearchObjectChunk,
    )

    def __init__(
        self,
        dbSessionCreator,
        statusController: StatusController,
        clientSearchObjectUpdateHandler: ClientSearchObjectChunkUpdateHandler,
    ):
        ACIProcessorQueueControllerABC.__init__(
            self, dbSessionCreator, _Notifier(statusController)
        )
        self._clientSearchObjectUpdateHandler: ClientSearchObjectChunkUpdateHandler = (
            clientSearchObjectUpdateHandler
        )

    def _sendToWorker(self, block: ACIProcessorQueueBlockItem):
        from peek_core_search._private.worker.tasks.SearchObjectChunkCompilerTask import (
            compileSearchObjectChunk,
        )

        return compileSearchObjectChunk.delay(block.itemsEncodedPayload)

    def _processWorkerResults(self, results):
        self._clientSearchObjectUpdateHandler.sendChunks(results)

    def _dedupeQueueSql(self, lastFetchedId: int, dedupeLimit: int):
        return """
                 with sq_raw as (
                    SELECT "id", "chunkKey"
                    FROM core_search."SearchObjectCompilerQueue"
                    WHERE id > %(id)s
                    LIMIT %(limit)s
                ), sq as (
                    SELECT min(id) as "minId", "chunkKey"
                    FROM sq_raw
                    GROUP BY  "chunkKey"
                    HAVING count("chunkKey") > 1
                )
                DELETE
                FROM core_search."SearchObjectCompilerQueue"
                     USING sq sq1
                WHERE core_search."SearchObjectCompilerQueue"."id" != sq1."minId"
                    AND core_search."SearchObjectCompilerQueue"."id" > %(id)s
                    AND core_search."SearchObjectCompilerQueue"."chunkKey" = sq1."chunkKey"

            """ % {
            "id": lastFetchedId,
            "limit": dedupeLimit,
        }

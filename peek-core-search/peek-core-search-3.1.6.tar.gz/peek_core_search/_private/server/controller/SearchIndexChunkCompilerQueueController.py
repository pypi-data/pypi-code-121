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
from peek_core_search._private.server.client_handlers.ClientSearchIndexChunkUpdateHandler import (
    ClientSearchIndexChunkUpdateHandler,
)
from peek_core_search._private.server.controller.StatusController import (
    StatusController,
)
from peek_core_search._private.storage.EncodedSearchIndexChunk import (
    EncodedSearchIndexChunk,
)
from peek_core_search._private.storage.SearchIndex import SearchIndex
from peek_core_search._private.storage.SearchIndexCompilerQueue import (
    SearchIndexCompilerQueue,
)

logger = logging.getLogger(__name__)


class _Notifier(ACIProcessorStatusNotifierABC):
    def __init__(self, adminStatusController: StatusController):
        self._adminStatusController = adminStatusController

    def setProcessorStatus(self, state: bool, queueSize: int):
        self._adminStatusController.status.searchIndexCompilerQueueStatus = state
        self._adminStatusController.status.searchIndexCompilerQueueSize = queueSize
        self._adminStatusController.notify()

    def addToProcessorTotal(self, delta: int):
        self._adminStatusController.status.searchIndexCompilerQueueProcessedTotal += (
            delta
        )
        self._adminStatusController.notify()

    def setProcessorError(self, error: str):
        self._adminStatusController.status.searchIndexCompilerQueueLastError = error
        self._adminStatusController.notify()


class SearchIndexChunkCompilerQueueController(ACIProcessorQueueControllerABC):
    QUEUE_ITEMS_PER_TASK = 10
    POLL_PERIOD_SECONDS = 1.000

    # We can run this with a large queue because this compiler only runs when the
    # object compiler queue is empty
    QUEUE_BLOCKS_MAX = 40
    QUEUE_BLOCKS_MIN = 4

    WORKER_TASK_TIMEOUT = 60.0

    _logger = logger
    _QueueDeclarative: ACIProcessorQueueTupleABC = SearchIndexCompilerQueue
    _VacuumDeclaratives = (
        SearchIndexCompilerQueue,
        SearchIndex,
        EncodedSearchIndexChunk,
    )

    def __init__(
        self,
        dbSessionCreator,
        statusController: StatusController,
        clientSearchIndexUpdateHandler: ClientSearchIndexChunkUpdateHandler,
        isProcessorEnabledCallable: Callable,
    ):
        ACIProcessorQueueControllerABC.__init__(
            self,
            dbSessionCreator,
            _Notifier(statusController),
            isProcessorEnabledCallable,
        )

        self._clientSearchIndexUpdateHandler: ClientSearchIndexChunkUpdateHandler = (
            clientSearchIndexUpdateHandler
        )

    def _sendToWorker(self, block: ACIProcessorQueueBlockItem):
        from peek_core_search._private.worker.tasks.SearchIndexChunkCompilerTask import (
            compileSearchIndexChunk,
        )

        return compileSearchIndexChunk.delay(block.itemsEncodedPayload)

    def _processWorkerResults(self, results):
        self._clientSearchIndexUpdateHandler.sendChunks(results)

    def _dedupeQueueSql(self, lastFetchedId: int, dedupeLimit: int):
        return """
                 with sq_raw as (
                    SELECT "id", "chunkKey"
                    FROM core_search."SearchIndexCompilerQueue"
                    WHERE id > %(id)s
                    LIMIT %(limit)s
                ), sq as (
                    SELECT min(id) as "minId", "chunkKey"
                    FROM sq_raw
                    GROUP BY  "chunkKey"
                    HAVING count("chunkKey") > 1
                )
                DELETE
                FROM core_search."SearchIndexCompilerQueue"
                     USING sq sq1
                WHERE core_search."SearchIndexCompilerQueue"."id" != sq1."minId"
                    AND core_search."SearchIndexCompilerQueue"."id" > %(id)s
                    AND core_search."SearchIndexCompilerQueue"."chunkKey" = sq1."chunkKey"

            """ % {
            "id": lastFetchedId,
            "limit": dedupeLimit,
        }

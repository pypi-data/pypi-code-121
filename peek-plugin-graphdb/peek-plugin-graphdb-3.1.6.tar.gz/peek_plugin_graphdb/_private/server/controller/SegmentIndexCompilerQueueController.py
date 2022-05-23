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
from peek_plugin_graphdb._private.server.client_handlers.SegmentChunkIndexUpdateHandler import (
    SegmentChunkIndexUpdateHandler,
)
from peek_plugin_graphdb._private.server.controller.StatusController import (
    StatusController,
)
from peek_plugin_graphdb._private.storage.GraphDbCompilerQueue import (
    GraphDbCompilerQueue,
)
from peek_plugin_graphdb._private.storage.GraphDbEncodedChunk import GraphDbEncodedChunk
from peek_plugin_graphdb._private.storage.GraphDbSegment import GraphDbSegment

logger = logging.getLogger(__name__)


class _Notifier(ACIProcessorStatusNotifierABC):
    def __init__(self, adminStatusController: StatusController):
        self._adminStatusController = adminStatusController

    def setProcessorStatus(self, state: bool, queueSize: int):
        self._adminStatusController.status.segmentCompilerQueueStatus = state
        self._adminStatusController.status.segmentCompilerQueueSize = queueSize
        self._adminStatusController.notify()

    def addToProcessorTotal(self, delta: int):
        self._adminStatusController.status.segmentCompilerQueueProcessedTotal += delta
        self._adminStatusController.notify()

    def setProcessorError(self, error: str):
        self._adminStatusController.status.segmentCompilerQueueLastError = error
        self._adminStatusController.notify()


class SegmentIndexCompilerQueueController(ACIProcessorQueueControllerABC):
    QUEUE_ITEMS_PER_TASK = 10
    POLL_PERIOD_SECONDS = 1.000

    QUEUE_BLOCKS_MAX = 20
    QUEUE_BLOCKS_MIN = 4

    WORKER_TASK_TIMEOUT = 60.0

    _logger = logger
    _QueueDeclarative: ACIProcessorQueueTupleABC = GraphDbCompilerQueue
    _VacuumDeclaratives = (GraphDbCompilerQueue, GraphDbEncodedChunk, GraphDbSegment)

    def __init__(
        self,
        dbSessionCreator,
        statusController: StatusController,
        clientChunkUpdateHandler: SegmentChunkIndexUpdateHandler,
    ):
        ACIProcessorQueueControllerABC.__init__(
            self, dbSessionCreator, _Notifier(statusController)
        )

        self._clientChunkUpdateHandler: SegmentChunkIndexUpdateHandler = (
            clientChunkUpdateHandler
        )

    def _sendToWorker(self, block: ACIProcessorQueueBlockItem):
        from peek_plugin_graphdb._private.worker.tasks.SegmentIndexCompiler import (
            compileSegmentChunk,
        )

        return compileSegmentChunk.delay(block.itemsEncodedPayload)

    def _processWorkerResults(self, results):
        self._clientChunkUpdateHandler.sendChunks(results)

    def _dedupeQueueSql(self, lastFetchedId: int, dedupeLimit: int):
        return """
                 with sq_raw as (
                    SELECT "id", "chunkKey"
                    FROM pl_graphdb."GraphDbChunkQueue"
                    WHERE id > %(id)s
                    LIMIT %(limit)s
                ), sq as (
                    SELECT min(id) as "minId", "chunkKey"
                    FROM sq_raw
                    GROUP BY  "chunkKey"
                    HAVING count("chunkKey") > 1
                )
                DELETE
                FROM pl_graphdb."GraphDbChunkQueue"
                     USING sq sq1
                WHERE pl_graphdb."GraphDbChunkQueue"."id" != sq1."minId"
                    AND pl_graphdb."GraphDbChunkQueue"."id" > %(id)s
                    AND pl_graphdb."GraphDbChunkQueue"."chunkKey" = sq1."chunkKey"

            """ % {
            "id": lastFetchedId,
            "limit": dedupeLimit,
        }

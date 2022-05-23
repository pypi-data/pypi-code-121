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
from peek_core_docdb._private.server.client_handlers.ClientChunkUpdateHandler import (
    ClientChunkUpdateHandler,
)
from peek_core_docdb._private.server.controller.StatusController import StatusController
from peek_core_docdb._private.storage.DocDbCompilerQueue import DocDbCompilerQueue
from peek_core_docdb._private.storage.DocDbDocument import DocDbDocument
from peek_core_docdb._private.storage.DocDbEncodedChunk import DocDbEncodedChunk

logger = logging.getLogger(__name__)


class _Notifier(ACIProcessorStatusNotifierABC):
    def __init__(self, adminStatusController: StatusController):
        self._adminStatusController = adminStatusController

    def setProcessorStatus(self, state: bool, queueSize: int):
        self._adminStatusController.status.documentCompilerQueueStatus = state
        self._adminStatusController.status.documentCompilerQueueSize = queueSize
        self._adminStatusController.notify()

    def addToProcessorTotal(self, delta: int):
        self._adminStatusController.status.documentCompilerQueueProcessedTotal += delta
        self._adminStatusController.notify()

    def setProcessorError(self, error: str):
        self._adminStatusController.status.documentCompilerQueueLastError = error
        self._adminStatusController.notify()


class ChunkCompilerQueueController(ACIProcessorQueueControllerABC):
    """DocDbChunkCompilerQueueController

    Compile the disp items into the grid data

    1) Query for queue
    2) Process queue
    3) Delete from queue

    """

    QUEUE_ITEMS_PER_TASK = 10
    POLL_PERIOD_SECONDS = 1.000

    QUEUE_BLOCKS_MAX = 20
    QUEUE_BLOCKS_MIN = 4

    WORKER_TASK_TIMEOUT = 60.0

    _logger = logger
    _QueueDeclarative: ACIProcessorQueueTupleABC = DocDbCompilerQueue
    _VacuumDeclaratives = (DocDbCompilerQueue, DocDbDocument, DocDbEncodedChunk)

    def __init__(
        self,
        dbSessionCreator,
        statusController: StatusController,
        clientChunkUpdateHandler: ClientChunkUpdateHandler,
    ):
        ACIProcessorQueueControllerABC.__init__(
            self, dbSessionCreator, _Notifier(statusController)
        )

        self._clientChunkUpdateHandler: ClientChunkUpdateHandler = (
            clientChunkUpdateHandler
        )

    def _sendToWorker(self, block: ACIProcessorQueueBlockItem):
        from peek_core_docdb._private.worker.tasks.ChunkCompilerTask import (
            compileDocumentChunk,
        )

        return compileDocumentChunk.delay(block.itemsEncodedPayload)

    def _processWorkerResults(self, results):
        self._clientChunkUpdateHandler.sendChunks(results)

    def _dedupeQueueSql(self, lastFetchedId: int, dedupeLimit: int):
        return """
                 with sq_raw as (
                    SELECT "id", "chunkKey"
                    FROM core_docdb."DocDbChunkQueue"
                    WHERE id > %(id)s
                    LIMIT %(limit)s
                ), sq as (
                    SELECT min(id) as "minId", "chunkKey"
                    FROM sq_raw
                    GROUP BY  "chunkKey"
                    HAVING count("chunkKey") > 1
                )
                DELETE
                FROM core_docdb."DocDbChunkQueue"
                     USING sq sq1
                WHERE core_docdb."DocDbChunkQueue"."id" != sq1."minId"
                    AND core_docdb."DocDbChunkQueue"."id" > %(id)s
                    AND core_docdb."DocDbChunkQueue"."chunkKey" = sq1."chunkKey"

            """ % {
            "id": lastFetchedId,
            "limit": dedupeLimit,
        }

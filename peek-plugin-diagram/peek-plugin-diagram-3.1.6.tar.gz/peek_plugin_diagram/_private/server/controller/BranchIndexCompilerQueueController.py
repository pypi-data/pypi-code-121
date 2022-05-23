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
from peek_plugin_diagram._private.server.client_handlers.BranchIndexChunkUpdateHandler import (
    BranchIndexChunkUpdateHandler,
)
from peek_plugin_diagram._private.server.controller.StatusController import (
    StatusController,
)
from peek_plugin_diagram._private.storage.branch.BranchIndex import BranchIndex
from peek_plugin_diagram._private.storage.branch.BranchIndexCompilerQueue import (
    BranchIndexCompilerQueue,
)
from peek_plugin_diagram._private.storage.branch.BranchIndexEncodedChunk import (
    BranchIndexEncodedChunk,
)

logger = logging.getLogger(__name__)


class _Notifier(ACIProcessorStatusNotifierABC):
    def __init__(self, adminStatusController: StatusController):
        self._adminStatusController = adminStatusController

    def setProcessorStatus(self, state: bool, queueSize: int):
        self._adminStatusController.status.branchIndexCompilerQueueStatus = state
        self._adminStatusController.status.branchIndexCompilerQueueSize = queueSize
        self._adminStatusController.notify()

    def addToProcessorTotal(self, delta: int):
        self._adminStatusController.status.branchIndexCompilerProcessedTotal += delta
        self._adminStatusController.notify()

    def setProcessorError(self, error: str):
        self._adminStatusController.status.branchIndexCompilerLastError = error
        self._adminStatusController.notify()


class BranchIndexCompilerQueueController(ACIProcessorQueueControllerABC):
    QUEUE_ITEMS_PER_TASK = 10
    POLL_PERIOD_SECONDS = 1.000

    QUEUE_BLOCKS_MAX = 20
    QUEUE_BLOCKS_MIN = 4

    WORKER_TASK_TIMEOUT = 60.0

    _logger = logger
    _QueueDeclarative: ACIProcessorQueueTupleABC = BranchIndexCompilerQueue
    _VacuumDeclaratives = (
        BranchIndexCompilerQueue,
        BranchIndex,
        BranchIndexEncodedChunk,
    )

    def __init__(
        self,
        dbSessionCreator,
        statusController: StatusController,
        clientUpdateHandler: BranchIndexChunkUpdateHandler,
    ):
        ACIProcessorQueueControllerABC.__init__(
            self, dbSessionCreator, _Notifier(statusController)
        )

        self._clientUpdateHandler: BranchIndexChunkUpdateHandler = clientUpdateHandler

    def _sendToWorker(self, block: ACIProcessorQueueBlockItem):
        from peek_plugin_diagram._private.worker.tasks.branch.BranchIndexCompiler import (
            compileBranchIndexChunk,
        )

        return compileBranchIndexChunk.delay(block.itemsEncodedPayload)

    def _processWorkerResults(self, results):
        self._clientUpdateHandler.sendChunks(results)

    def _dedupeQueueSql(self, lastFetchedId: int, dedupeLimit: int):
        return """
                 with sq_raw as (
                    SELECT "id", "chunkKey"
                    FROM pl_diagram."BranchIndexCompilerQueue"
                    WHERE id > %(id)s
                    LIMIT %(limit)s
                ), sq as (
                    SELECT min(id) as "minId", "chunkKey"
                    FROM sq_raw
                    GROUP BY  "chunkKey"
                    HAVING count("chunkKey") > 1
                )
                DELETE
                FROM pl_diagram."BranchIndexCompilerQueue"
                     USING sq sq1
                WHERE pl_diagram."BranchIndexCompilerQueue"."id" != sq1."minId"
                    AND pl_diagram."BranchIndexCompilerQueue"."id" > %(id)s
                    AND pl_diagram."BranchIndexCompilerQueue"."chunkKey" = sq1."chunkKey"

            """ % {
            "id": lastFetchedId,
            "limit": dedupeLimit,
        }

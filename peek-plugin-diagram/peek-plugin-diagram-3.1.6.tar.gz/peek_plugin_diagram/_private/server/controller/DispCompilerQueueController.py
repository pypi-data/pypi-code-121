import logging
from typing import List

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
from peek_plugin_diagram._private.server.controller.StatusController import (
    StatusController,
)
from peek_plugin_diagram._private.storage.DispIndex import (
    DispIndexerQueue as DispIndexerQueueTable,
)
from peek_plugin_diagram._private.storage.Display import (
    DispBase,
    DispNull,
    DispGroup,
    DispPolyline,
    DispGroupPointer,
    DispPolygon,
    DispEdgeTemplate,
    DispText,
    DispEllipse,
)
from peek_plugin_diagram._private.storage.LiveDbDispLink import LiveDbDispLink
from vortex.DeferUtil import deferToThreadWrapWithLogger

logger = logging.getLogger(__name__)


class _Notifier(ACIProcessorStatusNotifierABC):
    def __init__(self, adminStatusController: StatusController):
        self._adminStatusController = adminStatusController

    def setProcessorStatus(self, state: bool, queueSize: int):
        self._adminStatusController.status.displayCompilerQueueStatus = state
        self._adminStatusController.status.displayCompilerQueueSize = queueSize
        self._adminStatusController.notify()

    def addToProcessorTotal(self, delta: int):
        self._adminStatusController.status.displayCompilerProcessedTotal += delta
        self._adminStatusController.notify()

    def setProcessorError(self, error: str):
        self._adminStatusController.status.displayCompilerLastError = error
        self._adminStatusController.notify()


class DispCompilerQueueController(ACIProcessorQueueControllerABC):
    QUEUE_ITEMS_PER_TASK = 500
    POLL_PERIOD_SECONDS = 0.200

    QUEUE_BLOCKS_MAX = 20
    QUEUE_BLOCKS_MIN = 4

    WORKER_TASK_TIMEOUT = 60.0

    DEDUPE_LOOK_AHEAD_MIN_ROWS = 10 * 6  # a million rows
    DEDUPE_PERIOD_SECONDS: float = 60.0

    _logger = logger
    _QueueDeclarative: ACIProcessorQueueTupleABC = DispIndexerQueueTable
    _VacuumDeclaratives = (
        DispIndexerQueueTable,
        DispBase,
        DispNull,
        DispText,
        DispPolygon,
        DispPolyline,
        DispEllipse,
        DispGroup,
        DispEdgeTemplate,
        DispGroupPointer,
        LiveDbDispLink,
    )

    def __init__(self, dbSessionCreator, statusController: StatusController):
        ACIProcessorQueueControllerABC.__init__(
            self, dbSessionCreator, _Notifier(statusController)
        )

    def _sendToWorker(self, block: ACIProcessorQueueBlockItem):
        from peek_plugin_diagram._private.worker.tasks.DispCompilerTask import (
            compileDisps,
        )

        return compileDisps.delay(block.itemsEncodedPayload)

    def _processWorkerResults(self, results):
        pass

    # ---------------
    # Deduplicate methods

    def _dedupeQueueSql(self, lastFetchedId: int, dedupeLimit: int):
        return """
                 with sq_raw as (
                    SELECT "id", "dispId"
                    FROM pl_diagram."DispCompilerQueue"
                    WHERE id > %(id)s
                    LIMIT %(limit)s
                ), sq as (
                    SELECT min(id) as "minId", "dispId"
                    FROM sq_raw
                    GROUP BY  "dispId"
                    HAVING count("dispId") > 1
                )
                DELETE
                FROM pl_diagram."DispCompilerQueue"
                     USING sq sq1
                WHERE pl_diagram."DispCompilerQueue"."id" != sq1."minId"
                    AND pl_diagram."DispCompilerQueue"."id" > %(id)s
                    AND pl_diagram."DispCompilerQueue"."dispId" = sq1."dispId"

            """ % {
            "id": lastFetchedId,
            "limit": dedupeLimit,
        }

    # ---------------
    # Insert into Queue methods

    @deferToThreadWrapWithLogger(logger)
    def queueDisps(self, dispIds):
        return self.queueDispIdsToCompile(dispIds, self._dbSessionCreator)

    @classmethod
    def queueDispIdsToCompile(cls, dispIdsToCompile: List[int], dbSessionCreator):
        if not dispIdsToCompile:
            return

        ormSession = dbSessionCreator()
        try:
            cls.queueDispIdsToCompileWithSession(dispIdsToCompile, ormSession)
            ormSession.commit()

        finally:
            ormSession.close()

    @staticmethod
    def queueDispIdsToCompileWithSession(dispIdsToCompile: List[int], ormSessionOrConn):
        if not dispIdsToCompile:
            return

        logger.debug("Queueing %s disps for compile", len(dispIdsToCompile))

        inserts = []
        for dispId in dispIdsToCompile:
            inserts.append(dict(dispId=dispId))

        ormSessionOrConn.execute(DispIndexerQueueTable.__table__.insert(), inserts)

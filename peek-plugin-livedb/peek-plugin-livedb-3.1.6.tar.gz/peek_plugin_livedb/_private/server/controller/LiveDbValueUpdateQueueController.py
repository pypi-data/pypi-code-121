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
from peek_plugin_livedb._private.server.controller.AdminStatusController import (
    AdminStatusController,
)
from peek_plugin_livedb._private.storage.LiveDbItem import LiveDbItem
from peek_plugin_livedb._private.storage.LiveDbModelSet import getOrCreateLiveDbModelSet
from peek_plugin_livedb._private.storage.LiveDbRawValueQueue import LiveDbRawValueQueue
from peek_plugin_livedb.tuples.LiveDbRawValueUpdateTuple import (
    LiveDbRawValueUpdateTuple,
)
from vortex.DeferUtil import deferToThreadWrapWithLogger

logger = logging.getLogger(__name__)


class _Notifier(ACIProcessorStatusNotifierABC):
    def __init__(self, adminStatusController: AdminStatusController):
        self._adminStatusController = adminStatusController

    def setProcessorStatus(self, state: bool, queueSize: int):
        self._adminStatusController.status.rawValueQueueStatus = state
        self._adminStatusController.status.rawValueQueueSize = queueSize
        self._adminStatusController.notify()

    def addToProcessorTotal(self, delta: int):
        self._adminStatusController.status.rawValueProcessedTotal += delta
        self._adminStatusController.notify()

    def setProcessorError(self, error: str):
        self._adminStatusController.status.rawValueLastError = error
        self._adminStatusController.notify()


class LiveDbValueUpdateQueueController(ACIProcessorQueueControllerABC):
    # Prioritize the livedb updater.
    MAX_CPU_PERCENTAGE = 85.00

    QUEUE_ITEMS_PER_TASK = 500
    POLL_PERIOD_SECONDS = 0.200

    QUEUE_BLOCKS_MAX = 20
    QUEUE_BLOCKS_MIN = 4

    WORKER_TASK_TIMEOUT = 60.0

    _logger = logger
    _QueueDeclarative: ACIProcessorQueueTupleABC = LiveDbRawValueQueue
    _VacuumDeclaratives = (LiveDbRawValueQueue, LiveDbItem)

    def __init__(self, ormSessionCreator, adminStatusController: AdminStatusController):
        ACIProcessorQueueControllerABC.__init__(
            self, ormSessionCreator, _Notifier(adminStatusController)
        )

        self._modelSetIdByKey = {}

    def _sendToWorker(self, block: ACIProcessorQueueBlockItem):
        from peek_plugin_livedb._private.worker.tasks.LiveDbItemUpdateTask import (
            updateValues,
        )

        return updateValues.delay(block.itemsEncodedPayload)

    def _processWorkerResults(self, results):
        pass

    # ---------------
    # Deduplicate method

    def _dedupeQueueSql(self, lastFetchedId: int, dedupeLimit: int):
        """Deduplicate Queue

        NOTE: In this SQL, we take the last value added to the queue, as it will have
        the latest value.

        """
        return """
                 with sq_raw as (
                    SELECT "id", "modelSetId", "key"
                    FROM pl_livedb."LiveDbRawValueQueue"
                    WHERE id > %(id)s
                    LIMIT %(limit)s
                ), sq as (
                    -- Select the latest queued update, this does require that updates
                    -- come in, in order
                    SELECT max(id) as "maxId", "modelSetId", "key"
                    FROM sq_raw
                    GROUP BY  "modelSetId", "key"
                    HAVING count("key") > 1
                )
                DELETE
                FROM pl_livedb."LiveDbRawValueQueue"
                     USING sq sq1
                WHERE pl_livedb."LiveDbRawValueQueue"."id" != sq1."maxId"
                    AND pl_livedb."LiveDbRawValueQueue"."id" > %(id)s
                    AND pl_livedb."LiveDbRawValueQueue"."modelSetId" = sq1."modelSetId"
                    AND pl_livedb."LiveDbRawValueQueue"."key" = sq1."key"
                    
            """ % {
            "id": lastFetchedId,
            "limit": dedupeLimit,
        }

    # ---------------
    # Insert into Queue methods

    @deferToThreadWrapWithLogger(logger)
    def queueData(self, modelSetKey: str, updates: List[LiveDbRawValueUpdateTuple]):
        if not updates:
            return

        ormSession = self._dbSessionCreator()
        try:
            logger.debug("Queueing %s raw values for compile", len(updates))

            if modelSetKey not in self._modelSetIdByKey:
                modelSet = getOrCreateLiveDbModelSet(
                    ormSession, modelSetKey=modelSetKey
                )
                self._modelSetIdByKey[modelSet.key] = modelSet.id

            modelSetId = self._modelSetIdByKey[modelSetKey]

            inserts = []
            for update in updates:
                inserts.append(
                    dict(
                        modelSetId=modelSetId, key=update.key, rawValue=update.rawValue
                    )
                )

            ormSession.execute(LiveDbRawValueQueue.__table__.insert(), inserts)
            ormSession.commit()

        finally:
            ormSession.close()

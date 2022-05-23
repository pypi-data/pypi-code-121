import os
import typing
from abc import ABCMeta, abstractmethod
from collections import deque, namedtuple
from datetime import datetime, timedelta
from logging import Logger
from random import random
from time import sleep
from typing import List, Deque, Callable, Optional

import psutil
import pytz
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, ISOLATION_LEVEL_DEFAULT
from sqlalchemy import select, asc
from sqlalchemy.dialects import postgresql
from twisted.internet import task, reactor, defer
from twisted.internet.defer import inlineCallbacks, Deferred, DeferredSemaphore
from vortex.DeferUtil import (
    deferToThreadWrapWithLogger,
    vortexLogFailure,
    nonConcurrentMethod,
)
from vortex.Payload import Payload

from peek_abstract_chunked_index.private.server.controller.ACIProcessorStatusNotifierABC import (
    ACIProcessorStatusNotifierABC,
)
from peek_abstract_chunked_index.private.tuples.ACIProcessorQueueTupleABC import (
    ACIProcessorQueueTupleABC,
)
from peek_plugin_base.storage.RunPyInPg import runPyInPg

ACIProcessorQueueBlockItem = namedtuple(
    "ACIProcessorQueueBlockItem", ("queueIds", "itemsEncodedPayload", "itemUniqueIds")
)


class ACIProcessorQueueControllerABC(metaclass=ABCMeta):
    """Chunked Index Processor - Queue Controller

    Process the database queue and send chunks of data to the workers
    to process.

    1) Query for queue
    2) Process queue
    3) Delete from queue

    Example code :

        _logger = logger
        _QueueTableDeclarative = LiveDbRawValueQueueTuple

    """

    MAX_CPU_PERCENTAGE = 80.00

    QUEUE_ITEMS_PER_TASK: int = None  # Example 500
    POLL_PERIOD_SECONDS: float = None  # Example 0.200

    QUEUE_BLOCKS_MAX: int = None  # Example 40
    QUEUE_BLOCKS_MIN: int = None  # Example 8

    WORKER_TASK_TIMEOUT: int = None  # Example 60

    DEDUPE_LOOK_AHEAD_MIN_ROWS = 100000

    _logger: Logger = None
    _QueueDeclarative: ACIProcessorQueueTupleABC = None

    #: The queue controller will periodically vacuum these tables
    _VacuumDeclaratives: typing.Tuple[typing.Any] = None
    VACUUM_PERIOD_SECONDS: int = 60 * 60  # Every hour

    # Use at most 2 database connections at a time for vacuuming
    __vacuumSemaphore = DeferredSemaphore(2)

    def __init__(
        self,
        ormSessionCreator,
        processorStatusNotifier: ACIProcessorStatusNotifierABC,
        isProcessorEnabledCallable: Callable = None,
    ):
        self._dbSessionCreator = ormSessionCreator
        self._processorStatusNotifier: ACIProcessorStatusNotifierABC = (
            processorStatusNotifier
        )
        self._isProcessorEnabledCallable = isProcessorEnabledCallable

        self._pollLoopingCall = task.LoopingCall(self._poll)
        self._nextVacuumTime = datetime.now(pytz.utc) + self._randomiseTimeDelta(
            self.VACUUM_PERIOD_SECONDS
        )
        self._queueCount = 0

        self._queueIdsInBuffer = set()
        self._chunksInProgress = set()
        self._lastFetchedId = None

        self._pausedForDuplicate = None
        self._fetchedBlockBuffer: Deque[ACIProcessorQueueBlockItem] = deque()

        self._process = psutil.Process(os.getpid())

        assert self.QUEUE_ITEMS_PER_TASK, "ACI, QUEUE_ITEMS_PER_TASK is missing"
        assert self.POLL_PERIOD_SECONDS, "ACI, POLL_PERIOD_SECONDS is missing"
        assert self.QUEUE_BLOCKS_MAX, "ACI, QUEUE_BLOCKS_MAX is missing"
        assert self.QUEUE_BLOCKS_MIN is not None, "ACI, QUEUE_BLOCKS_MIN is missing"
        assert self.WORKER_TASK_TIMEOUT, "ACI, WORKER_TASK_TIMEOUT is missing"
        assert self._logger, "ACI, _logger is missing"
        assert self._QueueDeclarative, "ACI, _QueueDeclarative is missing"
        assert (
            self.DEDUPE_LOOK_AHEAD_MIN_ROWS
        ), "ACI, DEDUPE_LOOK_AHEAD_MIN_ROWS is missing"
        assert self._VacuumDeclaratives, "ACI, _VacuumDeclaratives is missing"
        assert self.VACUUM_PERIOD_SECONDS, "ACI, VACUUM_PERIOD_SECONDS is missing"

    def _randomiseTimeDelta(self, seconds: int) -> timedelta:
        # Randomise the time delta by up to +/- 20%
        delta = seconds * 0.20 * (random() - 0.5)
        return timedelta(seconds=seconds + delta)

    def isBusy(self) -> bool:
        return self._queueCount != 0

    def isQueueEmpty(self) -> bool:
        return self._queueCount == 0

    def start(self):
        self._processorStatusNotifier.setProcessorStatus(True, self._queueCount)
        d = self._pollLoopingCall.start(self.POLL_PERIOD_SECONDS, now=False)
        d.addCallbacks(self._timerCallback, self._timerErrback)

    def _timerErrback(self, failure):
        vortexLogFailure(failure, self._logger)
        self._processorStatusNotifier.setProcessorStatus(False, self._queueCount)
        self._processorStatusNotifier.setProcessorError(str(failure.value))

    def _timerCallback(self, _):
        self._processorStatusNotifier.setProcessorStatus(False, self._queueCount)

    def stop(self):
        if self._pollLoopingCall and self._pollLoopingCall.running:
            self._pollLoopingCall.stop()
            self._pollLoopingCall = None

    def shutdown(self):
        self.stop()

    @inlineCallbacks
    def _poll(self):
        # If the Queue processor is paused, then do nothing.
        if self._pausedForDuplicate:
            return

        # If we have a callable that can suspend this processor, then check it.
        if self._isProcessorEnabledCallable and not self._isProcessorEnabledCallable():
            return

        # We queue the grids in bursts, reducing the work we have to do.
        if self._queueCount > self.QUEUE_BLOCKS_MIN:
            return

        # If the CPU usage for this python process is too high, then skip this round
        num = self._process.cpu_percent()
        if self.MAX_CPU_PERCENTAGE < num:
            self._logger.debug("Skipping this loop, CPU is too high: %s", num)
            return

        fetchedBlocks = yield self._fetchBlocks()
        # Queue the next blocks
        self._fetchedBlockBuffer.extend(fetchedBlocks)

        # If we have nothing to do, exit now
        if not self._fetchedBlockBuffer:
            return

        # Process the block buffer
        while self._fetchedBlockBuffer:
            # Look at the next block to process
            block = self._fetchedBlockBuffer[0]

            # If we're already processing these chunks, then return and try later
            if self._chunksInProgress & block.itemUniqueIds:
                self._pausedForDuplicate = block.itemUniqueIds
                break

            # We're going to process it, remove it from the buffer
            self._fetchedBlockBuffer.popleft()

            # This should never fail
            d = self._runWorkerTask(block)
            d.addErrback(vortexLogFailure, self._logger)

            self._queueCount += 1
            if self._queueCount >= self.QUEUE_BLOCKS_MAX:
                break

        self._processorStatusNotifier.setProcessorStatus(True, self._queueCount)

        # Vacuum in the background
        d = self._vacuumTables()
        d.addErrback(vortexLogFailure, self._logger, consumeError=True)

    @inlineCallbacks
    def _runWorkerTask(self, block: ACIProcessorQueueBlockItem):

        startTime = datetime.now(pytz.utc)

        # Add the chunks we're processing to the set
        self._chunksInProgress |= block.itemUniqueIds

        try:
            d = self._sendToWorker(block)
            d.addTimeout(self.WORKER_TASK_TIMEOUT, reactor)

            results = yield d
            yield self._processWorkerResults(results)

            self._logger.debug(
                "Processed %s items, Time Taken = %s",
                len(block.itemUniqueIds),
                datetime.now(pytz.utc) - startTime,
            )

            # Success, Remove the chunks from the in-progress queue
            self._queueCount -= 1
            self._chunksInProgress -= block.itemUniqueIds
            self._queueIdsInBuffer -= set(block.queueIds)

            # If the queue processor was paused for this chunk then resume it.
            if (
                self._pausedForDuplicate
                and self._pausedForDuplicate & block.itemUniqueIds
            ):
                self._pausedForDuplicate = None

            # Notify the status controller
            self._processorStatusNotifier.setProcessorStatus(True, self._queueCount)
            self._processorStatusNotifier.addToProcessorTotal(len(block.itemUniqueIds))

        except Exception as e:
            if isinstance(e, defer.TimeoutError):
                self._logger.info("Retrying process, Task has timed out.")
            else:
                self._logger.warning("Retrying process : %s", str(e))

            reactor.callLater(2.0, self._runWorkerTask, block)
            return

    @abstractmethod
    def _sendToWorker(self, block: ACIProcessorQueueBlockItem) -> Deferred:
        """ Send to Worker

        This method calls the worker tasks, and resturns the deferred.
        Do not wait for the deferred and do any processing of the results here,
        do that instead in _processWorkerResults.

        Example code:

        def _sendToWorker(self, block: _BlockItem) -> Deferred:
            from peek_plugin_example._private.worker.tasks.ItemUpdateTask import \
                itemUpdateTask

            # Return the deferred, this is important
            return itemUpdateTask.delay(block.queueIds, block.itemsEncodedPayload)

        """

    @abstractmethod
    def _processWorkerResults(self, results):
        """Process Worker Results

        This method allows the inherting class to do something with the worker results.

        Example code:

        @inlineCallbacks
        def _processWorkerResults(self, results) -> Deferred:
            yield doSomethingWithResult(result)

        """

    @inlineCallbacks
    def _fetchBlocks(self) -> List[ACIProcessorQueueBlockItem]:

        dedupSql = (
            self._dedupeQueueSql(self._lastFetchedId, self.DEDUPE_LOOK_AHEAD_MIN_ROWS)
            if self._lastFetchedId
            else None
        )

        rawBlocks = yield runPyInPg(
            self._logger,
            self._dbSessionCreator,
            self._fetchBlocksInPg,
            None,
            list(self._queueIdsInBuffer),
            self._queueCount,
            dedupSql,
        )

        blocks = []
        for raw in rawBlocks:
            block = ACIProcessorQueueBlockItem(raw[0], raw[1].encode(), set(raw[2]))
            blocks.append(block)
            self._queueIdsInBuffer.update(block.queueIds)

        if self._queueIdsInBuffer:
            self._lastFetchedId = max(self._queueIdsInBuffer)

        return blocks

    @classmethod
    def _fetchBlocksInPg(
        cls, plpy, queueIdsInBuffer: List[int], queueCount: int, dedupSql: Optional[str]
    ) -> List[ACIProcessorQueueBlockItem]:
        # ---------------
        # Deduplicate the queue before we fetch more
        if dedupSql:
            plpy.execute(dedupSql)

        # ---------------
        # Prepare the input data
        queueIdsInBuffer = set(queueIdsInBuffer)

        # ---------------
        # Prepare the SQL
        queueTable = cls._QueueDeclarative.__table__

        toGrab = cls.QUEUE_BLOCKS_MAX - queueCount
        toGrab *= cls.QUEUE_ITEMS_PER_TASK

        # This is sorted with the newest queue item first for "USE LAST ITEM"
        # deduplication
        sql = select([queueTable]).order_by(asc(queueTable.c.id)).limit(toGrab)

        sqlQry = str(
            sql.compile(
                dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}
            )
        )

        # ---------------
        # Turn a row["val"] into a row.val
        class Wrap:
            row = None

            def __getattr__(self, name):
                return self.row[name]

        wrap = Wrap()

        # ---------------
        # Iterate through and load the tuples
        queueItems: List = []

        cursor = plpy.cursor(sqlQry)
        while True:
            rows = cursor.fetch(1000)
            if not rows:
                break
            for row in rows:
                wrap.row = row
                if wrap.id not in queueIdsInBuffer:
                    queueItems.append(cls._QueueDeclarative.sqlCoreLoad(wrap))

        # ---------------
        # Process the queue items int blocks

        # NOTE: Do not mess with this "USE LAST ITEM" deduplication strategy
        # Some plugins include values in their queues and we want the latest
        # value.
        queueItems = list(reversed(queueItems))
        addedUniqueKeys = set()

        queueBlocks = []
        for start in range(0, len(queueItems), cls.QUEUE_ITEMS_PER_TASK):

            queueIds = []
            itemUniqueIds = []
            items = []
            for item in queueItems[start : start + cls.QUEUE_ITEMS_PER_TASK]:
                queueIds.append(item.id)
                if item.ckiUniqueKey in addedUniqueKeys:
                    continue

                addedUniqueKeys.add(item.ckiUniqueKey)
                items.append(item)
                itemUniqueIds.append(item.ckiUniqueKey)

            itemsEncodedPayload = Payload(tuples=[items, queueIds]).toEncodedPayload()

            queueBlocks.append((queueIds, itemsEncodedPayload.decode(), itemUniqueIds))

        # Put the oldest queue blocks back at the start
        queueBlocks = list(reversed(queueBlocks))

        return queueBlocks

    @abstractmethod
    def _dedupeQueueSql(self, lastFetchedId: int, dedupeLimit: int):
        """Deduplicate Queue SQL

        This method will look ahead and deduplicate the queue before this class loads
        up the data.

        Example code #1:

            def _dedupeQueueSql(self, lastFetchedId: int, dedupeLimit: int):
                # Disable the dedupe process
                pass


        Example code #2:

            def _dedupeQueueSql(self, lastFetchedId: int, dedupeLimit: int):
                 return '''
                     with sq_raw as (
                        SELECT "id", "gridKey"
                        FROM pl_diagram."GridKeyCompilerQueue"
                        WHERE id > %(id)s
                        LIMIT %(limit)s
                    ), sq as (
                        SELECT min(id) as "minId", "gridKey"
                        FROM sq_raw
                        GROUP BY "gridKey"
                        HAVING count("gridKey") > 1
                    )
                    DELETE
                    FROM pl_diagram."GridKeyCompilerQueue"
                         USING sq sq1
                    WHERE pl_diagram."GridKeyCompilerQueue"."id" != sq1."minId"
                        AND pl_diagram."GridKeyCompilerQueue"."id" > %(id)s
                        AND pl_diagram."GridKeyCompilerQueue"."gridKey" = sq1."gridKey"
                ''' % {'id': self._lastQueueId, 'limit': dedupeLimit}


        """

    # ---------------
    # Vacuum Table methods

    @nonConcurrentMethod
    def _vacuumTables(self):
        if datetime.now(pytz.utc) < self._nextVacuumTime:
            return defer.succeed(True)

        self._nextVacuumTime = datetime.now(pytz.utc) + self._randomiseTimeDelta(
            self.VACUUM_PERIOD_SECONDS
        )

        return self.__vacuumSemaphore.run(
            deferToThreadWrapWithLogger(self._logger)(self.__vacuumTablesWrapped)
        )

    def __vacuumTablesWrapped(self):
        """Vacuum Tables

        This method will vacuum the tables in Post

        This query will take approximately 32ms for a queue of 10,000

        """

        for Declarative_ in self._VacuumDeclaratives:
            if not self._pollLoopingCall:
                return

            schema = Declarative_.__table__.schema
            tableName = Declarative_.__table__.name

            rawConn = self._dbSessionCreator.bind.raw_connection()
            rawConn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = rawConn.cursor()
            try:

                self._logger.debug("Vacuuming Table %s.%s", schema, tableName)
                cursor.execute('VACUUM FULL VERBOSE "%s"."%s"' % (schema, tableName))

                while len(rawConn.notices) < 2:
                    sleep(2.0)
                self._logger.debug(rawConn.notices[1].replace("\n", ", "))

            except Exception as e:
                self._logger.error("Vacuum failed for Table %s.%s", schema, tableName)
                self._logger.exception(e)

            finally:
                rawConn.set_isolation_level(ISOLATION_LEVEL_DEFAULT)
                rawConn.close()
                cursor.close()

    # ---------------
    # Insert into Queue methods
    #
    # These are custom in the controllers, because they can be quite custom.
    # Some don't even have insert methods in the controller, they are done from the
    # worker.

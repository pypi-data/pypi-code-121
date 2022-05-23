"""txcelery
Copyright Sentimens Research Group, LLC
2014
MIT License

Module Contents:
    - DeferredTask
    - CeleryClient
"""
import logging

import redis
from celery.exceptions import TimeoutError
from twisted.internet import defer, reactor
from twisted.internet.defer import inlineCallbacks, DeferredSemaphore
from twisted.internet.threads import deferToThread
from twisted.python.failure import Failure

logger = logging.getLogger(__name__)


class _DeferredTaskPatch(defer.Deferred):
    """Subclass of `twisted.defer.Deferred` that wraps a
    `celery.local.PromiseProxy` (i.e. a "Celery task"), exposing the combined
    functionality of both classes.

    `_DeferredTask` instances can be treated both like ordinary Deferreds and
    oridnary PromiseProxies.
    """

    #: Wait Period
    MAX_RETRIES = 3

    __reactorShuttingDown = False
    __dbSessionCreator = None
    __sqlaUrl = None
    __deferredSemaphore: DeferredSemaphore = None

    @classmethod
    def setupPostGreSQLConnection(
        cls, dbSessionCreator, sqlaUrl: str, parallelism: int
    ):
        """Start Celery Threads

        Configure the Celery connection settings.
        :param dbSessionCreator: A callable that will fiv.

        :param sqlaUrl: The connection string the SQLA Engine in PostGreSQL will use.

        :param parallelism: The number of tasks to run in parallel at one time

        """
        _DeferredTaskPatch.__dbSessionCreator = dbSessionCreator
        _DeferredTaskPatch.__sqlaUrl = sqlaUrl
        _DeferredTaskPatch.__deferredSemaphore = DeferredSemaphore(parallelism)

        from txcelery import defer

        defer._DeferredTask = _DeferredTaskPatch

        reactor.addSystemEventTrigger("before", "shutdown", cls.setReactorShuttingDown)

    @classmethod
    def setReactorShuttingDown(cls):
        cls.__reactorShuttingDown = True

    def __init__(self, func, *args, **kwargs):
        """Instantiate a `_DeferredTask`.  See `help(_DeferredTask)` for details
        pertaining to functionality.

        :param async_result : celery.result.AsyncResult
            AsyncResult to be monitored.  When completed or failed, the
            _DeferredTask will callback or errback, respectively.
        """
        # Deferred is an old-style class
        defer.Deferred.__init__(self, self._canceller)
        self.addErrback(self._cbErrback)

        # Auto initialise the the thread pool if the app hasn't already done so

        self.__retries = self.MAX_RETRIES

        d = self._start(func, *args, **kwargs)
        d.addBoth(self._threadFinishInMain)

    @inlineCallbacks
    def _start(self, func, *args, **kwargs):
        while self.__retries and not self.called and not self.__reactorShuttingDown:
            self.__retries -= 1
            try:
                result = yield self.__deferredSemaphore.run(
                    deferToThread, self._run, func, *args, **kwargs
                )
                return result

            except Exception as e:
                if not self.__retries:
                    print(e.__class__.__name__)
                    print(e)
                    raise

    def addTimeout(self, timeout, clock, onTimeoutCancel=None):
        defer.Deferred.addTimeout(self, timeout, clock, onTimeoutCancel=onTimeoutCancel)

    def _threadFinishInMain(self, result):
        if self.called:
            return

        if isinstance(result, Failure):
            if result.check(redis.exceptions.ConnectionError) and self.__retries:
                self.__retries -= 1

            self.errback(result)

        else:
            self.callback(result)

    def _canceller(self, *args):
        self.__retries = 0

    def _cbErrback(self, failure: Failure) -> Failure:
        if isinstance(failure.value, TimeoutError):
            self._canceller()

        return failure

    def _run(self, func, *args, **kwargs):
        """Monitor Task In Thread

        The Celery task state must be checked in a thread, otherwise it blocks.

        This may stuff with Celerys connection to the result backend.
        I'm not sure how it manages that.

        """
        from peek_storage_service.plpython.RunWorkerTaskPyInPg import (
            runPyWorkerTaskInPgBlocking,
        )

        return runPyWorkerTaskInPgBlocking(
            self.__dbSessionCreator, self.__sqlaUrl, func, *args, **kwargs
        )

import logging
import typing

import celery
from celery import signals as celery_signals
from kombu import serialization
from peek_platform.file_config.PeekFileConfigWorkerMixin import (
    PeekFileConfigWorkerMixin,
)
from vortex.DeferUtil import noMainThread
from vortex.Payload import Payload

logger = logging.getLogger(__name__)


def vortexDumps(arg: typing.Tuple) -> str:
    noMainThread()
    # startTime = datetime.now(pytz.utc)
    try:
        return Payload(tuples=[arg])._toJson()
    except Exception as e:
        logger.exception(e)
        raise
    # finally:
    #     logger.debug("vortexDumps took %s", (datetime.now(pytz.utc) - startTime))


def vortexLoads(jsonStr: str) -> typing.Tuple:
    noMainThread()
    # startTime = datetime.now(pytz.utc)
    try:
        return Payload()._fromJson(jsonStr).tuples[0]
    except Exception as e:
        logger.exception(e)
        raise
    # finally:
    #     logger.debug("vortexLoads took %s", (datetime.now(pytz.utc) - startTime))


serialization.register(
    "vortex",
    vortexDumps,
    vortexLoads,
    content_type="application/x-vortex",
    content_encoding="utf-8",
)


# -----------------------------------------------------------------------------


class BackendMixin:
    def exception_to_python(self, exc):
        """Convert serialized exception to Python exception."""
        import sys
        from kombu.utils.encoding import from_utf8
        from celery.utils.serialization import (
            create_exception_cls,
            get_pickled_exception,
        )

        EXCEPTION_ABLE_CODECS = frozenset({"pickle"})

        if not exc:
            return exc

        if not isinstance(exc, BaseException):
            exc_module = exc.get("exc_module")
            if exc_module is None:
                cls = create_exception_cls(from_utf8(exc["exc_type"]), __name__)
            else:
                exc_module = from_utf8(exc_module)
                exc_type = from_utf8(exc["exc_type"])
                try:
                    cls = getattr(sys.modules[exc_module], exc_type)
                except KeyError:
                    cls = create_exception_cls(exc_type, celery.exceptions.__name__)
            exc_msg = exc["exc_message"]
            args = exc_msg if isinstance(exc_msg, tuple) else [exc_msg]

            ### BEGIN CODE ADDED TO PATCH METHOD
            try:
                exc = cls(*args)

            except TypeError:
                exc = Exception("%s\n%s" % (cls, args))
            ### END CODE ADDED TO PATCH METHOD

            if self.serializer in EXCEPTION_ABLE_CODECS:
                exc = get_pickled_exception(exc)

        return exc


from celery.backends.base import Backend

Backend.exception_to_python = BackendMixin.exception_to_python


# -----------------------------------------------------------------------------


class ResultConsumerMixin:
    def cancel_for(self, task_id):
        import redis

        if not self._pubsub:
            return

        key = self._get_key_for_task(task_id)
        self.subscribed_to.discard(key)

        try:
            self._pubsub.unsubscribe(key)

        except redis.exceptions.ConnectionError:
            # redis.exceptions.ConnectionError: Error 32 while writing to socket. Broken pipe.
            logger.debug("Cancel_for failed due to redis error")

        except RuntimeError:
            # builtins.RuntimeError: dictionary changed size during iteration
            logger.debug("Cancel_for failed due to redis error")

        except AttributeError:
            # builtins.AttributeError: 'NoneType' object has no attribute 'sendall'
            logger.debug("Cancel_for failed due to redis error")


from celery.backends.redis import ResultConsumer

ResultConsumer.cancel_for = ResultConsumerMixin.cancel_for


# -----------------------------------------------------------------------------


def configureCeleryApp(
    app, workerConfig: PeekFileConfigWorkerMixin, forCaller: bool = False
):
    # Optional configuration, see the application user guide.
    app.conf.update(
        # On peek_logic_service, the thread limit is set to 10, these should be configurable.
        # broker_pool_limit=20,
        # Set the broker and backend URLs
        broker_url=workerConfig.celeryBrokerUrl,
        result_backend=workerConfig.celeryResultUrl,
        # Leave the logging to us
        worker_hijack_root_logger=False,
        # The time results will stay in redis before expiring.
        # I believe they are cleared when the results are obtained
        # from txcelery._DeferredTask
        # I assume the timer only starts once the task has finished.
        result_expires=60,
        task_serializer="vortex",
        # accept_content=['vortex'],  # Ignore other content
        accept_content=["pickle", "json", "msgpack", "yaml", "vortex"],
        result_serializer="vortex",
        enable_utc=True,
        # Default time in seconds before a retry of the task should be executed.
        # 3 minutes by default.
        default_retry_delay=2,
        # The maximum number of times to retry a task
        max_retries=5,
    )

    # Configure these only for the worker, this keeps the servers json clean.
    if not forCaller:
        # Optional configuration, see the application user guide.
        app.conf.update(
            # The number of tasks each worker will prefetch.
            worker_prefetch_multiplier=workerConfig.celeryTaskPrefetch,
            # The number of workers to have at one time
            worker_concurrency=workerConfig.celeryWorkerCount,
        )

        if workerConfig.celeryReplaceWorkerAfterTaskCount:
            app.conf.update(
                # The number of tasks a worker will process before it's replaced
                worker_max_tasks_per_child=workerConfig.celeryReplaceWorkerAfterTaskCount,
            )

        if workerConfig.celeryReplaceWorkerAfterMemUsage:
            app.conf.update(
                # If a worker uses more than this amount of memory, it will be replaced
                # after the task completes.
                worker_max_memory_per_child=workerConfig.celeryReplaceWorkerAfterMemUsage,
            )


from peek_platform.file_config.PeekFileConfigABC import PeekFileConfigABC
from peek_platform.file_config.PeekFileConfigPlatformMixin import (
    PeekFileConfigPlatformMixin,
)


class _WorkerTaskConfigMixin(PeekFileConfigABC, PeekFileConfigPlatformMixin):
    pass


@celery_signals.after_setup_logger.connect
def configureCeleryLogging(*args, **kwargs):
    from peek_plugin_base.PeekVortexUtil import peekWorkerName

    # Fix the loading problems windows has
    # from peek_platform.util.LogUtil import setupPeekLogger
    # setupPeekLogger(peekWorkerName)

    from peek_platform import PeekPlatformConfig

    PeekPlatformConfig.componentName = peekWorkerName
    config = _WorkerTaskConfigMixin()

    # Set default logging level
    logging.root.setLevel(config.loggingLevel)

    if config.loggingLevel != "DEBUG":
        for name in ("celery.worker.strategy", "celery.app.trace", "celery.worker.job"):
            logging.getLogger(name).setLevel(logging.WARNING)

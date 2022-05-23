import logging
import multiprocessing
from typing import Optional

from jsoncfg.value_mappers import require_string, require_integer, require_bool

logger = logging.getLogger(__name__)


class PeekFileConfigWorkerMixin:
    @property
    def celeryBrokerUrl(self) -> str:
        # for BROKER_URL
        default = "amqp://guest:guest@localhost:5672//"
        with self._cfg as c:
            return c.celery.brokerUrl(default, require_string)

    @property
    def celeryResultUrl(self) -> str:
        # for CELERYD_CONCURRENCY
        default = "redis://localhost:6379/0"
        with self._cfg as c:
            return c.celery.resultUrl(default, require_string)

    @property
    def celeryWorkerCount(self) -> str:
        # for CELERYD_CONCURRENCY

        # By default, we assume a single server setup.
        # So leave half the CPU threads for the database
        default = int(multiprocessing.cpu_count() / 2)
        with self._cfg as c:
            return c.celery.worker.workerCount(default, require_integer)

    @property
    def celeryTaskPrefetch(self) -> str:
        # for CELERYD_PREFETCH_MULTIPLIER

        default = 2

        with self._cfg as c:
            return c.celery.worker.taskPrefetch(default, require_integer)

    @property
    def celeryReplaceWorkerAfterTaskCount(self) -> Optional[int]:
        # for worker_max_tasks_per_child
        with self._cfg as c:
            try:
                return int(c.celery.worker.refreshAfterTaskCount(None))
            except TypeError:
                return None
            except ValueError:
                return None

    @property
    def celeryReplaceWorkerAfterMemUsage(self) -> Optional[int]:
        # for worker_max_memory_per_child
        with self._cfg as c:
            try:
                return int(c.celery.worker.refreshAfterMemUsage(None))
            except TypeError:
                return None
            except ValueError:
                return None

    @property
    def celeryConnectionPoolSize(self) -> int:
        with self._cfg as c:
            return c.celery.caller.connectionPoolSize(50, require_integer)

    @property
    def celeryConnectionRecycleTime(self) -> int:
        with self._cfg as c:
            return c.celery.caller.connectionRecycleTime(600, require_integer)

    @property
    def celeryConnectionPoolSize(self) -> int:
        with self._cfg as c:
            return c.celery.caller.connectionPoolSize(50, require_integer)

    @property
    def celeryPlPythonEnablePatch(self) -> int:
        with self._cfg as c:
            return c.celery.plpython.enable(False, require_bool)

    @property
    def celeryPlPythonWorkerCount(self) -> int:
        with self._cfg as c:
            return c.celery.plpython.workerCount(6, require_integer)

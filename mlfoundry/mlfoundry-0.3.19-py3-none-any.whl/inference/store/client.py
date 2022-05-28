import atexit
import logging
import os
import queue
import threading
import typing

from mlfoundry.exceptions import MlFoundryException

from .constants import (
    FLUSH_BATCH_SIZE_ENV_VAR,
    FLUSH_INTERVAL_ENV_VAR,
    MAX_QUEUE_SIZE_ENV_VAR,
)
from .inference_packet import ActualPacket, InferencePacket
from .repositories import AbstractInferenceStore
from .worker import InferenceStoreWorker

if typing.TYPE_CHECKING:
    from .inference_packet import BasePacket

logger = logging.getLogger(__name__)


def _check_shutdown(func):
    def wrapper(self, *args, **kwargs):
        if self._is_shutdown:
            raise MlFoundryException("cannot execute after client is shutdown")
        return func(self, *args, **kwargs)

    return wrapper


class InferenceStoreClient:
    def __init__(
        self,
        inference_repository_maker: typing.Callable[..., AbstractInferenceStore],
    ):
        self._is_shutdown = False

        self.inference_store: AbstractInferenceStore = inference_repository_maker()

        max_queue_size = int(os.getenv(MAX_QUEUE_SIZE_ENV_VAR, "10000"))
        flush_interval = float(os.getenv(FLUSH_INTERVAL_ENV_VAR, "5"))
        flush_batch_size = int(os.getenv(FLUSH_BATCH_SIZE_ENV_VAR, "100"))

        if max_queue_size <= 0:
            raise MlFoundryException(
                f"{MAX_QUEUE_SIZE_ENV_VAR} should be a positive number"
            )

        self.task_queue: "queue.Queue[BasePacket]" = queue.Queue(max_queue_size)
        self.worker_terminate_event = threading.Event()

        if flush_interval <= 0:
            raise MlFoundryException(
                f"{FLUSH_INTERVAL_ENV_VAR} should be a positive number"
            )
        if flush_batch_size <= 0 or flush_batch_size > max_queue_size:
            raise MlFoundryException(
                f"{FLUSH_BATCH_SIZE_ENV_VAR} should be positive"
                f" and lower than {MAX_QUEUE_SIZE_ENV_VAR}"
            )

        self.worker: InferenceStoreWorker = InferenceStoreWorker(
            task_queue=self.task_queue,
            terminate_event=self.worker_terminate_event,
            inference_store=self.inference_store,
            flush_interval=flush_interval,
            flush_every_num_message=flush_batch_size,
        )
        atexit.register(self.shutdown)
        self.worker.start()

    def _put_in_queue(self, inference_packet: InferencePacket):
        try:
            self.task_queue.put_nowait(inference_packet)
        except queue.Full as ex:
            raise MlFoundryException(
                "task queue is full\n"
                f"current task queue length is {MAX_QUEUE_SIZE}\n"
                "consider increasing the task queue length using "
                f"{MAX_QUEUE_SIZE_ENV_VAR} environment variable"
            ) from ex

    @_check_shutdown
    def log_predictions(self, predictions: typing.List[InferencePacket]):
        for prediction in predictions:
            self._put_in_queue(prediction)

    @_check_shutdown
    def log_actuals(self, actuals: typing.List[ActualPacket]):
        for actual in actuals:
            self._put_in_queue(actual)

    def flush(self):
        logger.debug(
            f"flushing task queue, {self.task_queue.qsize()} items in the queue"
        )
        self.task_queue.join()
        logger.debug("task queue flushed")

    def shutdown(self):
        if self._is_shutdown:
            return
        logger.debug("shutting down worker and client")
        self._is_shutdown = True
        # NOTE: We initialize the inference store at first in the constructor
        # The task_queue, worker is defined later.
        # There is a chance that inference  store initialization will throw error,
        # in that case, shutdown will be called (__del__) but self.task_queue would not have
        # been initialized yet.
        if hasattr(self, "task_queue"):
            self.flush()
        if hasattr(self, "worker_terminate_event"):
            logger.debug("setting worker termination event")
            self.worker_terminate_event.set()
        if hasattr(self, "worker"):
            logger.debug("waiting for worker to terminate")
            self.worker.join()

    def __del__(self):
        self.shutdown()

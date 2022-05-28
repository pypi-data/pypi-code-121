import logging
import queue
import threading
import time
import typing

from .inference_packet import BasePacket
from .repositories import AbstractInferenceStore

logger = logging.getLogger(__name__)


class InferenceStoreWorker(threading.Thread):
    def __init__(
        self,
        task_queue: queue.Queue,
        terminate_event: threading.Event,
        inference_store: AbstractInferenceStore,
        flush_interval: float,
        flush_every_num_message: int,
    ):
        super().__init__(daemon=True)
        self.task_queue: "queue.Queue[BasePacket]" = task_queue
        self.terminate_event = terminate_event
        self.inference_store: AbstractInferenceStore = inference_store
        self.flush_interval: float = flush_interval
        self.flush_every_num_message: int = flush_every_num_message

    def next_batch_from_queue(self) -> typing.List[BasePacket]:
        batch = []

        start_time = time.monotonic()
        time_to_stop = start_time + self.flush_interval

        while len(batch) < self.flush_every_num_message:
            time_delta = time_to_stop - time.monotonic()
            if time_delta <= 0:
                logger.debug("flushing as time interval has reached")
                break
            try:
                inference_packet = self.task_queue.get(block=True, timeout=time_delta)
                batch.append(inference_packet)
            except queue.Empty:
                logger.debug("task queue is empty")

        return batch

    def work(self):
        inference_packets = self.next_batch_from_queue()
        if len(inference_packets) == 0:
            return
        try:
            self.inference_store.batch_log_inference(inference_packets)
        except Exception:
            logger.exception(
                "fail to log inference\n"
                f"discarding {len(inference_packets)} inference_packets"
            )
        for _ in range(len(inference_packets)):
            self.task_queue.task_done()

    def run(self):
        logger.debug("worker started")
        while not self.terminate_event.is_set():
            self.work()
        logger.debug("worker exited")

import logging
import queue
import threading
import time
from typing import Any, Dict

from mlflow.entities import Metric

from mlfoundry.background import utils as bg_utils
from mlfoundry.background.events import Event, LogMetricsEvent

logger = logging.getLogger(__name__)


class Interface(object):
    """
    Interface that facilitates communication between producing threads and consuming threads via an event queue
    """

    def __init__(
        self,
        run_id: str,
        event_queue: "queue.Queue[Event]",
    ):
        """
        Args:
            event_queue: queue to hold events
        """
        self.run_id = run_id
        self.event_queue = event_queue
        self._event_queue_closed = False

    def log_metrics(self, metric_dict: Dict[str, Any], step: int = 0) -> None:
        """
        Publish `metric_dict` as event to event queue which would be logged asynchronously

        Args:
            metric_dict: dict mapping key (string) to values (mostly float, int) to log as metrics
            step: step number or iteration number, defaults to zero
        """
        # TODO (chiragjn): Yuck! duplication between Run instance and this interface
        #                  We should start moving all logic to interface and make public log methods
        #                  on Run instance act as proxies with the option to be sync / async.
        if not metric_dict:
            return
        timestamp = int(time.time() * 1000)
        metrics_arr = [
            Metric(key, value, timestamp, step=step)
            for key, value in metric_dict.items()
        ]
        event = LogMetricsEvent(
            producer=threading.currentThread().getName(), metrics=metrics_arr
        )
        self.put_event(event)

    def put_event(self, event: Event) -> None:
        """
        Put the given `event` to event queue if the queue is not yet closed.

        Args:
            event: instance of `Event` or subclass of `Event`
        """
        if self._event_queue_closed:
            logger.warning(
                bg_utils.make_log(
                    f"put_event called with {event!r} after close. Dropping event"
                )
            )
            return
        logger.debug(bg_utils.make_log(f"enqueue_event {event!r}"))
        self.event_queue.put(event)

    def get_event(self, **get_kwargs) -> Event:
        """
        Pop and get `Event` from event queue

        Args:
            **get_kwargs: kwargs to forward to `queue.Queue.get`

        Returns:
            Event: instance of `Event` or subclass of `Event`

        Raises:
            queue.Empty: if the event queue is empty
        """
        try:
            event = self.event_queue.get(**get_kwargs)
            logger.debug(bg_utils.make_log(f"dequeue_event {event!r}"))
            return event
        except queue.Empty:
            raise

    def close(self) -> None:
        """
        Mark the event queue as closed to stop accepting more events
        """
        self._event_queue_closed = True

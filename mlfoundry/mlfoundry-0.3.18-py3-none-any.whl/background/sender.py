import logging
import queue
from timeit import default_timer
from typing import Any, List, Optional

from mlflow.entities import Metric
from mlflow.exceptions import MlflowException
from mlflow.tracking import MlflowClient

from mlfoundry import MlFoundryException
from mlfoundry.background import utils as bg_utils
from mlfoundry.background.events import LogMetricsEvent
from mlfoundry.background.interface import Interface

logger = logging.getLogger(__name__)


class SenderJob(bg_utils.BackgroundJob):
    name_prefix = "MLFSenderThread"

    def __init__(
        self,
        interface: Interface,
        mlflow_client: MlflowClient,
        interval: float,
    ):
        """
        Args:
            interface: `background.interface.Interface` instance to use to get and log events with
            interval: time in seconds to sleep between calls to `self._loop` i.e. between iterations
        """
        super().__init__(
            name=f"{SenderJob.name_prefix}:{interface.run_id}", interval=interval
        )
        self._mlflow_client = mlflow_client
        self._interface = interface

    def _log_metrics(self, metrics: List[Metric]) -> None:
        """
        Log metrics using the MlFlowClient instance

        Args:
            metrics: list of mlflow.entities.metric.Metric instances

        Raises:
            MlFoundryException: in case .log_batch call fails
        """
        try:
            self._mlflow_client.log_batch(
                run_id=self._interface.run_id, metrics=metrics
            )
        except MlflowException as e:
            raise MlFoundryException(e.message).with_traceback(
                e.__traceback__
            ) from None

    def join(self, timeout: Optional[int] = None) -> None:
        """
        Wait for event queue to be empty and then join on self (thread)
        Note: This should not be called from the Sender Thread itself otherwise will cause a deadlock

        Args:
            timeout: time in seconds to wait when joining
        """
        start = default_timer()
        self._interface.event_queue.join()
        time_elapsed = default_timer() - start
        time_left = None if timeout is None else max(0.0, timeout - time_elapsed)
        super().join(timeout=time_left)

    def _consume_event(self) -> Any:
        """
        Consume a single event from the event queue and mark it done

        Returns:
            Any: ...

        Raises:
            queue.Empty: in case the event queue has no events
        """
        # TODO (chiragjn): implement batch consume
        event = self._interface.get_event(block=False)
        try:
            if isinstance(event, LogMetricsEvent):
                # TODO (chiragjn): Think of a better design to publish and consume events
                return self._log_metrics(metrics=event.metrics)
            else:
                logger.warning(
                    bg_utils.make_log(
                        f"Unknown Event of type {type(event)!r} emitted. Dropping event"
                    )
                )
        except Exception as e:
            logger.warning(
                bg_utils.make_log(
                    f"Encountered an internal error while trying to consume: {str(e)}"
                )
            )
        finally:
            self._interface.event_queue.task_done()

    def _loop(self) -> None:
        """
        Attempt to consume a single event from the event queue
        """
        try:
            self._consume_event()
        except queue.Empty:
            pass

    def _finish(self) -> None:
        """
        Consume remaining events in the event queue
        """
        while not self._interface.event_queue.empty():
            try:
                self._consume_event()
            except queue.Empty:
                break
        self._interface = None

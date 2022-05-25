import threading

from urllib3.exceptions import MaxRetryError

from openapi_client.models.experiment_progress_update_api_input import (
    ExperimentProgressUpdateAPIInput,
)
from vessl.util import logger
from vessl.util.api import VesslApi
from vessl.util.exception import VesslApiException

PROGRESS_UPDATE_INTERVAL_IN_SEC = 1


class ProgressUpdater(object):
    def __init__(self, api: VesslApi, experiment_id: int):
        self._api = api
        self._experiment_id = experiment_id
        self._thread = threading.Thread(target=self._thread_body, daemon=True)
        self._exit = threading.Event()

        self._progress = None

    def start(self):
        self._thread.start()

    def stop(self):
        self._exit.set()
        self._thread.join()

    def update(self, value: float):
        self._progress = value

    def _thread_body(self):
        while not self._exit.is_set():
            self._send()
            self._exit.wait(timeout=PROGRESS_UPDATE_INTERVAL_IN_SEC)
        self._send()

    def _send(self):
        if self._progress is None:
            return

        logger.debug(f"Sending experiment progress: {self._progress}")
        try:
            self._api.experiment_progress_update_api(
                self._experiment_id,
                experiment_progress_update_api_input=ExperimentProgressUpdateAPIInput(
                    progress_percent=self._progress,
                ),
            )
            self._progress = None  # Flush after sending

        except (MaxRetryError, VesslApiException) as e:
            logger.exception("Failed to send metrics to server", exc_info=e)

        except Exception as e:
            logger.exception("Unexpected error", exc_info=e)

import abc
import copy
import logging
import os
import threading
from enum import Enum
from logging import Logger
from typing import Dict, List, Optional, Set

from worker_bunch.dispatcher import Dispatcher, DispatcherListener
from worker_bunch.mqtt.mqtt_proxy import MqttProxy
from worker_bunch.notification import Notification
from worker_bunch.service_config import ConfigException
from worker_bunch.service_logging import ServiceLogging
from worker_bunch.utils.time_utils import TimeUtils


class ShutdownException(Exception):
    pass


class WorkerSetup(Enum):
    """keys used in `Worker.setup` kwargs"""
    ASTRAL_TIME_MANAGER = "astral_time_manager"
    BASE_DATA_DIR = "base_data_dir"
    DATABASE_MANAGER = "database_manager"
    MQTT_PROXY = "mqtt_proxy"
    WORKER_SETTINGS = "worker_settings"


class Worker(threading.Thread, DispatcherListener):

    def __init__(self, name: str):
        threading.Thread.__init__(self, name=name)

        self._setup_done = False

        self._lock = threading.Lock()
        self._closing = False  # shutdown in process
        self._base_data_dir: Optional[str] = None

        self.__logger: Optional[Logger] = None

        self._notifications: Set[Notification] = set()

        self._worker_settings: Dict[str, any] = {}
        self._mqtt_proxy: Optional[MqttProxy] = None

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, self.name)

    def __repr__(self) -> str:
        return '{}({})'.format(self.__class__.__name__, self.name)

    def setup(self, props: Dict[WorkerSetup, any]):
        with self._lock:
            if self._setup_done:
                raise RuntimeError(f"Setup only once ('{self.name}')!")
            self._setup_done = True

            self._base_data_dir = props.get(WorkerSetup.BASE_DATA_DIR)
            worker_settings = props.get(WorkerSetup.WORKER_SETTINGS)
            self._worker_settings = copy.deepcopy(worker_settings) if worker_settings else {}
            self._mqtt_proxy = props.get(WorkerSetup.MQTT_PROXY)

    def ensure_data_path(self, file_name: Optional[str] = None) -> str:
        if not self._base_data_dir:
            raise ConfigException(f"No data dir configured (but expected by '{self.name}')!")
        data_path = os.path.join(self._base_data_dir, self.name)  # base dir + worker name
        os.makedirs(data_path, exist_ok=True)
        if file_name:
            data_path = os.path.join(data_path, file_name)
        return data_path

    def get_partial_settings_schema(self) -> Optional[Dict[str, any]]:
        """returns a partial JSON schema for extra setting if needed. overwrite..."""
        return None

    def make_partial_settings_required(self) -> bool:
        """return True to force existence via JSON schema validation. overwrite..."""
        return False

    def set_last_will(self):
        """Set the last will at mqtt client. Explicitly triggered before the mqtt client connects. Kind of:
        ```
        if self._topic and self._last_will:
            self._mqtt_proxy.set_last_will(self._topic, self._last_will)
        ```
        """

    def stop(self):
        """
        Just the notification to finish and stop the thread. A last will may be better send within `_final_work`.
        """
        with self._lock:
            self._closing = True

    def proceed(self) -> bool:
        with self._lock:
            if self._closing:
                raise ShutdownException()
            return True

    @property
    def _logger(self):
        if self.__logger is None:
            log_name = ServiceLogging.get_log_name(self, self.name)
            self.__logger = logging.getLogger(log_name)
        return self.__logger

    # noinspection PyMethodMayBeStatic
    def _sleep(self):
        TimeUtils.sleep(0.5)

    @abc.abstractmethod
    def subscribe_notifications(self, dispatcher: Dispatcher):
        """
        subscribe for notifications via:

        timer_job = schedule.every(14 * 60).to(16 * 60).seconds  # type: schedule.Job
        dispatcher.subscribe_timer(self, timer_job, "keyword-timer")

        self._dispatcher.subscribe_cron("* * * * *", self, "cron-every-minute")

        self._dispatcher.subscribe_topics(self, ["mqtt/topic"],
        """
        raise NotImplementedError()

    def add_notifications(self, notifications: Set[Notification]):
        with self._lock:
            self._notifications |= notifications

    def _get_and_reset_notifications(self) -> List[Notification]:
        with self._lock:
            notifications = list(self._notifications)
            self._notifications.clear()
            return notifications

    def _should_handle_pending_notifications(self) -> bool:
        with self._lock:
            return bool(self._notifications)

    def run(self):
        try:
            while self.proceed():
                self._process_notifications()
                self._sleep()

        except ShutdownException:
            pass
        except Exception as ex:
            self._logger.exception(ex)
        finally:
            self._final_work()

    def run_single(self):
        try:
            if self.proceed():
                self._process_notifications()

        except ShutdownException:
            pass
        except Exception as ex:
            self._logger.exception(ex)
        finally:
            self._final_work()

    def _process_notifications(self):
        if self._should_handle_pending_notifications():
            notifications = self._get_and_reset_notifications()
            if notifications:
                self._work(notifications)

    @abc.abstractmethod
    def _work(self, notifications: List[Notification]):
        """the task "main" function."""
        raise NotImplementedError()

    def _final_work(self):
        """
        E.g.: You may send explicitly the last will(s) here (as a normal message). Kind of:
        ```
        if self._topic and self._last_will:
            self._mqtt_proxy.publish(self._topic, self._last_will)
        ```
        """

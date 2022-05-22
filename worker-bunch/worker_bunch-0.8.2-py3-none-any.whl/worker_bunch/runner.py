import asyncio
import logging
import signal
import threading
from asyncio import Task
from typing import List, Optional

from worker_bunch.dispatcher import Dispatcher
from worker_bunch.mqtt.mqtt_proxy import MqttProxy
from worker_bunch.notification import NotificationType
from worker_bunch.utils.time_utils import TimeUtils
from worker_bunch.worker.worker import Worker

_logger = logging.getLogger(__name__)


class Runner:

    TIME_LIMIT_MQTT_CONNECTION = 10  # seconds

    def __init__(self, dispatcher: Dispatcher, mqtt_proxy: MqttProxy, workers: List[Worker]):

        # init
        self._dispatcher = dispatcher
        self._mqtt_proxy = mqtt_proxy
        self._workers = workers

        self._loop = asyncio.get_event_loop()
        self._main_task = None  # type: Optional[Task]

        if threading.current_thread() is threading.main_thread():
            # integration tests may run the service in a thread...
            signal.signal(signal.SIGINT, self._shutdown_signaled)
            signal.signal(signal.SIGTERM, self._shutdown_signaled)

    def _shutdown_signaled(self, sig, _frame):
        _logger.info("shutdown signaled (%s)", sig)
        if self._main_task:
            self._main_task.cancel()

    def run(self):
        """endless loop"""

        # connect mqtt - part 1 - trigger
        self._mqtt_proxy.connect()

        self._main_task = self._loop.create_task(self._main_loop())

        try:
            self._loop.run_until_complete(self._main_task)
        except asyncio.CancelledError:
            _logger.debug("canceling...")

    def run_single(self):
        # connect mqtt - part 1 - trigger
        self._mqtt_proxy.connect()

        self._main_task = self._loop.create_task(self._main_single())

        self._loop.run_until_complete(self._main_task)

    async def _wait_for_mqtt_connection_timeout(self):
        timeout = self.TIME_LIMIT_MQTT_CONNECTION
        try:
            return await asyncio.wait_for(self._wait_for_mqtt_connection(), timeout)
        except asyncio.exceptions.TimeoutError:
            raise asyncio.exceptions.TimeoutError(f"couldn't connect to MQTT (within {timeout}s)!") from None

    async def _wait_for_mqtt_connection(self):
        """connect mqtt - part 2 - wait for connection and subscribe for topics"""
        while True:
            if self._mqtt_proxy.is_connected():
                for worker in self._workers:
                    worker.subscribe_notifications(self._dispatcher)

                topics = self._dispatcher.get_mqtt_topics()
                self._mqtt_proxy.subscribe(topics)
                break

            await asyncio.sleep(0.05)

    async def _main_loop(self):
        await self._wait_for_mqtt_connection_timeout()

        last_worker_check_time = TimeUtils.now()

        for worker in self._workers:
            worker.start()

        self._dispatcher.trigger_start_notification(self._workers)

        while True:
            self._mqtt_proxy.publish()

            self._mqtt_proxy.ensure_connection()
            messages = self._mqtt_proxy.get_messages()
            self._dispatcher.push_mqtt_messages(messages)

            self._dispatcher.trigger_timers()

            if (TimeUtils.now() - last_worker_check_time).total_seconds() > 20:
                last_worker_check_time = TimeUtils.now()
                dead_workers = [w.name for w in self._workers if not w.is_alive()]
                if dead_workers:
                    raise RuntimeError("Dead workers found: {}".format(", ".join(dead_workers)))

            await asyncio.sleep(0.05)

    async def _main_single(self):
        await self._wait_for_mqtt_connection_timeout()

        await asyncio.sleep(0.2)  # wait for messages to come in

        messages = self._mqtt_proxy.get_messages()
        self._dispatcher.push_mqtt_messages(messages)
        self._dispatcher.trigger_start_notification(self._workers, NotificationType.SINGLE_STARTED)

        await asyncio.sleep(0.2)  # wait for debounce pipelines to finish

        for worker in self._workers:
            worker.run_single()

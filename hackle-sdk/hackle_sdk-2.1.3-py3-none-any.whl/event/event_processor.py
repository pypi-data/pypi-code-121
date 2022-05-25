import threading
import time
from datetime import timedelta

from six.moves import queue

from hackle import logger as _logging
from hackle.event.event_dispatcher import EventDispatcher
from hackle.event.user_event import (UserEvent, ExposureEvent, TrackEvent)


class BatchEventProcessor(object):
    _DEFAULT_QUEUE_CAPACITY = 1000
    _DEFAULT_BATCH_SIZE = 1000
    _DEFAULT_FLUSH_INTERVAL = 10
    _DEFAULT_TIMEOUT_INTERVAL = 5
    _SHUTDOWN_SIGNAL = object()
    _FLUSH_SIGNAL = object()
    LOCK = threading.Lock()

    def __init__(self, sdk_key=None, event_dispatcher=None, logger=None):
        self.sdk_key = sdk_key
        self.event_dispatcher = event_dispatcher or EventDispatcher
        self.logger = _logging.adapt_logger(logger or _logging.NoOpLogger())
        self.event_queue = queue.Queue(maxsize=self._DEFAULT_QUEUE_CAPACITY)
        self.batch_size = self._DEFAULT_BATCH_SIZE
        self.flush_interval = timedelta(seconds=self._DEFAULT_FLUSH_INTERVAL)
        self.timeout_interval = timedelta(seconds=self._DEFAULT_TIMEOUT_INTERVAL)
        self._current_batch = list()

        self.executor = None
        self.start()

    @property
    def is_running(self):
        return self.executor.is_alive() if self.executor else False

    # noinspection PyMethodMayBeStatic
    def _get_time(self, _time=None):
        if _time is None:
            return time.time()

        return _time

    def start(self):
        if hasattr(self, 'executor') and self.is_running:
            self.logger.warn('BatchEventProcessor already started.')
            return

        self.flushing_interval_deadline = self._get_time() + self._get_time(self.flush_interval.total_seconds())
        self.executor = threading.Thread(target=self._run)
        self.executor.setDaemon(True)
        self.executor.start()

    def _run(self):
        try:
            while True:
                if self._get_time() >= self.flushing_interval_deadline:
                    self._flush_batch()
                    self.flushing_interval_deadline = self._get_time() + \
                                                      self._get_time(self.flush_interval.total_seconds())
                    self.logger.debug('Flush interval deadline. Flushed batch.')

                try:
                    interval = self.flushing_interval_deadline - self._get_time()
                    item = self.event_queue.get(True, interval)

                    if item is None:
                        continue

                except queue.Empty:
                    continue

                if item == self._SHUTDOWN_SIGNAL:
                    self.logger.debug('Shutdown')
                    break

                if item == self._FLUSH_SIGNAL:
                    self.logger.debug('Flush')
                    self._flush_batch()
                    continue

                if isinstance(item, UserEvent):
                    self._add_to_batch(item)

        except Exception as exception:
            self.logger.error('Uncaught exception in event processor: {}'.format(str(exception)))

        finally:
            self.logger.info('Exit Event Processing loop')
            self._flush_batch()

    def flush(self):
        self.event_queue.put(self._FLUSH_SIGNAL)

    def _flush_batch(self):
        batch_len = len(self._current_batch)
        if batch_len == 0:
            self.logger.debug('Noting to flush')
            return

        self.logger.debug('Flushing batch size {}'.format(str(batch_len)))

        with self.LOCK:
            to_process_batch = list(self._current_batch)
            self._current_batch = list()

        exposure_events = []
        track_events = []
        for event in to_process_batch:
            if isinstance(event, ExposureEvent):
                exposure_events.append(event)
            if isinstance(event, TrackEvent):
                track_events.append(event)

        events = {
            'exposureEvents': exposure_events,
            'trackEvents': track_events
        }

        try:
            self.logger.debug('Events : {}'.format(str(events)))
            self.event_dispatcher.dispatch_event(self.sdk_key, events)
        except Exception as exception:
            self.logger.error('Error dispatching event : {} {}'.format(str(events), str(exception)))

    def process(self, event):
        try:
            self.event_queue.put_nowait(event)
        except queue.Full:
            self.logger.debug('Queue is full. Current size : {}'.format(str(self.event_queue.qsize())))

    def _add_to_batch(self, event):
        if len(self._current_batch) == 0:
            self.flushing_interval_deadline = self._get_time() + self._get_time(self.flush_interval.total_seconds())

        with self.LOCK:
            self._current_batch.append(event)
        if len(self._current_batch) >= self.batch_size:
            self.logger.debug('Flushing batch size {}'.format(str(self.batch_size)))
            self._flush_batch()

    def stop(self):
        self.event_queue.put(self._SHUTDOWN_SIGNAL)

        if self.executor:
            self.executor.join(self.timeout_interval.total_seconds())

        if self.is_running:
            self.logger.error('Timeout exceeded {} ms.'.format(str(self.timeout_interval)))

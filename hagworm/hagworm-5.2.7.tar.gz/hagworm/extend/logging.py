# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import os
import sys
import queue
import logging

from threading import Thread
from datetime import timedelta
from loguru._file_sink import FileSink

from elasticsearch import Elasticsearch, helpers as es_helpers

from .base import Utils


class LogFileRotator:

    @classmethod
    def make(cls, _size=500, _time=r'00:00'):

        return cls(_size, _time).should_rotate

    def __init__(self, _size, _time):

        _size = _size * (1024 ** 2)
        _time = Utils.split_int(_time, r':')

        now_time = Utils.today()

        self._size_limit = _size
        self._time_limit = now_time.replace(hour=_time[0], minute=_time[1])

        if now_time >= self._time_limit:
            self._time_limit += timedelta(days=1)

    def should_rotate(self, message, file):

        file.seek(0, 2)

        if file.tell() + len(message) > self._size_limit:
            return True

        if message.record[r'time'].timestamp() > self._time_limit.timestamp():
            self._time_limit += timedelta(days=1)
            return True

        return False


DEFAULT_LOG_FILE_ROTATOR = LogFileRotator.make()


class LogInterceptor(logging.Handler):
    """日志拦截器
    """

    def emit(self, record):

        Utils.log.opt(
            depth=6,
            exception=record.exc_info
        ).log(
            record.levelname,
            record.getMessage()
        )


DEFAULT_LOG_INTERCEPTOR = LogInterceptor()


class ElasticsearchSink:
    """Elasticsearch日志投递
    """

    def __init__(self, hosts, index, *, topic=None, buffer_maxsize=0xffff, **kwargs):

        self._elasticsearch = Elasticsearch(hosts, **kwargs)
        self._index = index
        self._topic = Utils.uuid1() if topic is None else topic

        self._buffer = queue.Queue(buffer_maxsize)

        self._worker = Thread(target=self._queued_writer)
        self._running = True

        self._init_es_index()
        self._worker.start()

    def _init_es_index(self):

        indices = self._elasticsearch.indices

        if not indices.exists(index=self._index):

            indices.create(
                index=self._index,
                mappings={
                    r'properties': {
                        r'topic': {
                            r'type': r'keyword',
                            r'ignore_above': 64,
                        },
                        r'process': {
                            r'properties': {
                                r'id': {
                                    r'type': r'long',
                                },
                                r'name': {
                                    r'type': r'keyword',
                                    r'ignore_above': 64,
                                },
                            },
                        },
                        r'thread': {
                            r'properties': {
                                r'id': {
                                    r'type': r'long',
                                },
                                r'name': {
                                    r'type': r'keyword',
                                    r'ignore_above': 64,
                                },
                            },
                        },
                        r'level': {
                            r'properties': {
                                r'no': {
                                    r'type': r'integer',
                                },
                                r'name': {
                                    r'type': r'keyword',
                                    r'ignore_above': 64,
                                },
                            },
                        },
                        r'module': {
                            r'type': r'text',
                        },
                        r'message': {
                            r'type': r'text',
                            r'analyzer': r'ik_max_word',
                            r'search_analyzer': r'ik_smart',
                        },
                        r'datetime': {
                            r'type': r'date',
                            r'format': r'epoch_millis',
                        },
                    }
                }
            )

    def write(self, message):

        try:
            self._buffer.put(message, block=True, timeout=1)
        except queue.Full as _:
            if message.record[r'level'].no > logging.INFO:
                sys.stderr.write(str(message))

    def stop(self):

        self._running = False
        self._worker.join(10)

        super().stop()

    def _queued_writer(self):

        current_ident = self._worker.ident

        while self._running:

            try:

                records = [self._buffer.get(block=True, timeout=10).record]

                for _ in range(min(self._buffer.qsize(), 1000)):
                    records.append(self._buffer.get_nowait().record)

                if records:
                    es_helpers.bulk(
                        self._elasticsearch,
                        actions=[
                            {
                                r'_op_type': r'create',
                                r'_index': self._index,
                                r'topic': self._topic,
                                r'process': {
                                    r'id': _row[r'process'].id,
                                    r'name': _row[r'process'].name,
                                },
                                r'thread': {
                                    r'id': _row[r'thread'].id,
                                    r'name': _row[r'thread'].name,
                                },
                                r'level': {
                                    r'no': _row[r'level'].no,
                                    r'name': _row[r'level'].name,
                                },
                                r'module': f"{_row[r'name']}:{_row[r'function']}:{_row[r'line']}",
                                r'message': _row[r'message'],
                                r'datetime': int(_row[r'time'].timestamp() * 1000),
                            }
                            for _row in records if current_ident != _row[r'thread'].id
                        ]
                    )

            except queue.Empty as _:

                pass

            except Exception as err:

                sys.stderr.write(str(err))


class QueuedFileSink(FileSink):
    """日志文件队列
    """

    def __init__(self, path, *, buffer_maxsize=0xffff, **kwargs):

        super().__init__(path, **kwargs)

        self._buffer = queue.Queue(buffer_maxsize)

        self._worker = Thread(target=self._queued_writer)
        self._running = True

        self._worker.start()

    def write(self, message):

        try:
            self._buffer.put(message, block=True, timeout=1)
        except queue.Full as _:
            if message.record[r'level'].no > logging.INFO:
                sys.stderr.write(str(message))

    def stop(self):

        self._running = False
        self._worker.join(10)

        super().stop()

    def _queued_writer(self):

        while self._running:

            try:
                super().write(
                    self._buffer.get(block=True, timeout=10)
                )
            except queue.Empty as _:
                pass
            except Exception as err:
                sys.stderr.write(str(err))


DEFAULT_LOG_FILE_NAME = r'runtime_{time}.log'


def init_logger(
        level, handler=None,
        file_path=None, file_name=DEFAULT_LOG_FILE_NAME,
        file_rotation=DEFAULT_LOG_FILE_ROTATOR, file_retention=0xff,
        debug=False
):

    level = level.upper()

    Utils.log.remove()

    if handler or file_path:

        if handler:
            Utils.log.add(
                handler,
                level=level,
                enqueue=True,
                backtrace=debug
            )

        if file_path:

            _file_name, _file_ext_name = os.path.splitext(file_name)

            Utils.log.add(
                QueuedFileSink(
                    Utils.path.join(file_path, _file_name + '.pid-' + str(Utils.getpid()) + _file_ext_name),
                    rotation=file_rotation,
                    retention=file_retention
                ),
                level=level,
                enqueue=True,
                backtrace=debug
            )

    else:

        Utils.log.add(
            sys.stderr,
            level=level,
            enqueue=True,
            backtrace=debug
        )

    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(DEFAULT_LOG_INTERCEPTOR)

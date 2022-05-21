# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

from tempfile import TemporaryFile

from .base import Utils
from .task import IntervalTask

from ..interface import ContextManager


class _BufferAbstract:

    def __init__(self):

        self._buffer = []

    def _consume_buffer(self):
        pass

    def _get_buffer(self):

        if not self._buffer:
            return None

        buffer, self._buffer = self._buffer, []

        return buffer

    def size(self):

        return len(self._buffer)

    def append(self, data):

        self._buffer.append(data)
        self._consume_buffer()

    def extend(self, data_list):

        self._buffer.extend(data_list)
        self._consume_buffer()


class DataQueue(_BufferAbstract):

    def __init__(self, handler, task_limit=1):

        super().__init__()

        self._handler = handler

        self._tasks = set()

        self._task_limit = task_limit

    def _consume_buffer(self):

        while len(self._tasks) < self._task_limit:
            if not self._create_task():
                break

    def _create_task(self):

        if len(self._buffer) > 0:

            task = Utils.create_task(
                self._handler(
                    self._buffer.pop(0)
                )
            )

            task.add_done_callback(self._on_task_done)

            self._tasks.add(task)

            return True

        else:

            return False

    def _on_task_done(self, task):

        if task in self._tasks:
            self._tasks.remove(task)

        self._consume_buffer()


class QueueBuffer(_BufferAbstract):

    def __init__(self, handler, slice_size, timeout=1, task_limit=1):

        super().__init__()

        self._slice_size = slice_size
        self._data_queue = DataQueue(handler, task_limit)

        self._timer = IntervalTask.create(timeout, self._do_consume_buffer)
        self._timer.start()

    def _consume_buffer(self):

        if self.size() >= self._slice_size:
            self._do_consume_buffer()

    def _do_consume_buffer(self):

        buffer = self._get_buffer()

        if buffer:
            self._data_queue.append(buffer)


class FileBuffer(ContextManager):
    """文件缓存类
    """

    def __init__(self, slice_size=0x1000000):

        self._buffers = []

        self._slice_size = slice_size

        self._read_offset = 0

        self._append_buffer()

    def _context_release(self):

        self.close()

    def _append_buffer(self):

        self._buffers.append(TemporaryFile())

    def close(self):

        while len(self._buffers) > 0:
            self._buffers.pop(0).close()

        self._read_offset = 0

    def write(self, data):

        buffer = self._buffers[-1]

        buffer.seek(0, 2)
        buffer.write(data)

        if buffer.tell() >= self._slice_size:
            buffer.flush()
            self._append_buffer()

    def read(self, size=None):

        buffer = self._buffers[0]

        buffer.seek(self._read_offset, 0)

        result = buffer.read(size)

        if len(result) == 0 and len(self._buffers) > 1:
            self._buffers.pop(0).close()
            self._read_offset = 0
        else:
            self._read_offset = buffer.tell()

        return result

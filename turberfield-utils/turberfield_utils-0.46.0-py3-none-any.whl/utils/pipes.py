#!/usr/bin/env python3
#   encoding: UTF-8

# This file is part of turberfield.
#
# Turberfield is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Turberfield is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with turberfield.  If not, see <http://www.gnu.org/licenses/>.

import ast
import asyncio
import os
from pprint import pprint
import sys

__doc__ = """
The module provides interprocess Queues. Two variants are available;
one for use with an asyncio_ event loop, and one for code written in
a blocking-call style. Both variants accept the following Python
structures: strings, bytes, numbers, tuples, lists, dicts, sets,
booleans, and None.

The Queues are implemented with POSIX named pipes; this module
works only on those operating systems which support them.

.. _asyncio: https://docs.python.org/3/library/asyncio.html#module-asyncio
"""


class SimplePipeQueue:
    """
    :param path: supplies the path to the underlying POSIX named pipe.
    :param history: If True, a pipe which already exists will be
                    reused, and not removed after exiting the Queue.

    This class can send messages without blocking your code::

        pq = SimplePipeQueue.pipequeue("/tmp/pq.fifo")
        pq.put_nowait((0, "First message."))
        pq.close()

    You can also use this class as a context manager.
    Don't forget that
    :py:meth:`get() <turberfield.utils.pipes.SimplePipeQueue.get>`
    is a blocking operation::

        with SimplePipeQueue("/tmp/pq.fifo") as pq:
            msg = pq.get()

    """

    @classmethod
    def pipequeue(cls, *args, **kwargs):
        """
        This is a factory function which creates and initialises a
        Queue. Your code should call
        :py:meth:`close() <turberfield.utils.pipes.SimplePipeQueue.close>`
        on the queue when finished.
        """
        return cls(*args, **kwargs).__enter__()

    def __init__(self, path, history=True):
        self.path = path
        self.history = history

    def __enter__(self):
        try:
            os.mkfifo(self.path)
        except FileExistsError:
            if not self.history:
                raise

        fd = os.open(self.path, os.O_RDONLY | os.O_NONBLOCK)
        self._out = os.fdopen(fd, 'r', buffering=1, encoding="utf-8")
        self._in = open(self.path, "w", buffering=1, encoding="utf-8")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        if not self.history:
            os.remove(self.path)
        return False

    def put_nowait(self, msg):
        """
        Put an item into the queue without blocking.
        """
        try:
            pprint(msg, stream=self._in, compact=True, width=sys.maxsize)
        except TypeError:  # 'compact' is new in Python 3.4
            pprint(msg, stream=self._in, width=sys.maxsize)
        finally:
            self._in.flush()

    def get(self):
        """
        Remove and return an item from the queue. If queue is empty,
        block until an item is available.
        """
        payload = self._out.readline().rstrip("\n")
        return ast.literal_eval(payload)

    def close(self):
        """
        Completes the use of the queue.
        """
        self._out.close()
        self._in.close()


class PipeQueue(SimplePipeQueue):
    """
    :param path: supplies the path to the underlying POSIX named pipe.
    :param history: If True, a pipe which already exists will be
                    reused, and not removed after exiting the Queue.

    This is a subclass of
    :py:class:`SimplePipeQueue <turberfield.utils.pipes.SimplePipeQueue>`,
    extended for use like an `asyncio.Queue`_::

        pq = PipeQueue.pipequeue("/tmp/pq.fifo")
        yield from pq.put((0, "First message."))
        pq.close()

    and::

        pq = PipeQueue.pipequeue("/tmp/pq.fifo")
        msg = yield from pq.get()
        pq.close()

    .. _asyncio.Queue: https://docs.python.org/3/library/asyncio-queue.html#queue
    """

    @staticmethod
    def get_when_ready(fObj, q):
        payload = fObj.readline().rstrip("\n")
        q.put_nowait(ast.literal_eval(payload))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._q = asyncio.Queue()

    def __enter__(self):
        super().__enter__()

        fd = self._out.fileno()
        loop = asyncio.get_event_loop()
        loop.add_reader(fd, PipeQueue.get_when_ready, self._out, self._q)
        return self

    @asyncio.coroutine
    def get(self):
        """
        Remove and return an item from the queue. If queue is empty,
        wait until an item is available.

        This method is a coroutine_.

        .. _coroutine: https://docs.python.org/3/library/asyncio-task.html#coroutine
        """
        rv = yield from self._q.get()
        return rv

    @asyncio.coroutine
    def put(self, msg):
        """
        Put an item into the queue. If the queue is full, wait until
        a free slot is available before adding item.

        This method is a coroutine_.

        .. _coroutine: https://docs.python.org/3/library/asyncio-task.html#coroutine
        """
        future = asyncio.Future()
        self.put_nowait(msg)
        future.set_result(msg)
        return future

    def close(self):
        loop = asyncio.get_event_loop()
        loop.remove_reader(self._out.fileno())
        self._out.close()
        self._in.close()

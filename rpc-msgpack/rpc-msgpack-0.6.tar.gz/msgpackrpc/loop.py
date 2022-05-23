from tornado import ioloop
import asyncio


class Loop(object):
    """\
    An I/O loop class which wraps the Tornado's ioloop.
    """

    @staticmethod
    def instance():
        return Loop()

    def __init__(self, loop=None):
        try:
            """
            Create a new loop for every
            new thread besides main.
            """
            loop_ = asyncio.get_event_loop()
        except RuntimeError:
            loop_ = asyncio.new_event_loop()
            asyncio.set_event_loop(loop_)

        self._ioloop = loop or ioloop.IOLoop.current()
        self._asyncio_loop = loop_
        self._periodic_callback = None

    def start(self):
        """\
        Starts the Tornado's ioloop if it's not running.
        """

        self._ioloop.start()

    def stop(self):
        """\
        Stops the Tornado's ioloop if it's running.
        """

        self._ioloop.stop()

    def attach_periodic_callback(self, callback, callback_time):
        if self._periodic_callback is not None:
            self.dettach_periodic_callback()

        self._periodic_callback = ioloop.PeriodicCallback(callback, callback_time)
        self._periodic_callback.start()

    def dettach_periodic_callback(self):
        if self._periodic_callback is not None:
            self._periodic_callback.stop()
        self._periodic_callback = None

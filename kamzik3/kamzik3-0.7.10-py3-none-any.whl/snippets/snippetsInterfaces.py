from threading import Thread, Event


class CallbackTimerInterface(Thread):

    timeout = 0

    def __init__(self, timeout, callback, with_correction=True):
        """
        Callback timer.

        :param timeout: int (unit=milliseconds)
        :param callback: fun
        """
        assert callable(callback)
        self.callback = callback
        self.set_timeout(timeout)
        self.stopped = Event()
        self.with_correction = with_correction
        Thread.__init__(self)

    def set_timeout(self, timeout):
        self.timeout = timeout * 1e-3

    def run(self):
        raise NotImplementedError

    def stop(self):
        try:
            self.stopped.set()
            # self.join()
        except TypeError:
            pass

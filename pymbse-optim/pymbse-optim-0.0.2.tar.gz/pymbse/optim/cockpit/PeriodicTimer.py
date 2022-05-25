from threading import Timer


class PeriodicTimer:
    """ Class providing a repeated timer functionality used for updating the optimization cockpit

    """
    def __init__(self, t_sleep_in_sec: float, function) -> None:
        """ Constructor of a RepeatedTimer instance

        :param t_sleep_in_sec: interval of function execution (in seconds)
        :param function: function to be executed at regular intervals
        """
        self._timer = None
        self.interval = t_sleep_in_sec
        self.function = function
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function()

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

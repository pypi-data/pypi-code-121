from threading import Thread


class ReadlineThread(Thread):
    def __init__(self, input, handle_callback):
        Thread.__init__(self)
        self._input = input
        self._handle_callback = handle_callback

    def run(self):
        for line in self._input:
            self._handle_callback(line)

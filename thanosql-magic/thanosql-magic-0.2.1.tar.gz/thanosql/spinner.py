import threading
import time

from IPython.display import clear_output


class Spinner:
    busy = False
    delay = 0.1

    @staticmethod
    def spinning_cursor():
        while 1:
            yield from "|/-\\"

    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay):
            self.delay = delay

    def spinner_task(self):
        while self.busy:
            print("[+] Running...", next(self.spinner_generator))
            clear_output(wait=True)
            time.sleep(self.delay)

    def start(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def stop(self):
        self.busy = False
        time.sleep(self.delay)

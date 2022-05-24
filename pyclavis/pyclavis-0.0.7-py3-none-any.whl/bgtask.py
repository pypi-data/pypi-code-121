import os
import threading
from queue import Queue


class BackgroundTask(threading.Thread):
    def start(self):
        self.qu = Queue()
        self.rc = None
        super().start()

    def _append_rc(self, rc):
        print(rc)
        self.qu.put(rc)

    def pop(self):
        try:
            return self.qu.get(block=False)
        except:
            pass

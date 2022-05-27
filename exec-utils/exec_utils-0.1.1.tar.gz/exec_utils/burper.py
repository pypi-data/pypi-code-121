import threading


class Burper(threading.Thread):

    def __init__(self, stdin_bytes, stdin_handle):
        super().__init__()
        self.stdin_bytes = stdin_bytes
        self.stdin_handle = stdin_handle

    def run(self):
        try:
            self.stdin_handle.write(self.stdin_bytes)
        finally:
            self.stdin_handle.close()

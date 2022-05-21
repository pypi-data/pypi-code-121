import time
import threading


class BackgroundTasks(threading.Thread):
    def run(self, *args, **kwargs):
        while True:
            # self.create_backend_request(path="/poll-api", data={})
            time.sleep(1)

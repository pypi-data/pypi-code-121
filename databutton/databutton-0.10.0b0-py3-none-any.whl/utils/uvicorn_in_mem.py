import contextlib
import threading
import time

import uvicorn


class Server(uvicorn.Server):
    is_finished = False

    def install_signal_handlers(self):
        pass

    @contextlib.contextmanager
    def run_in_thread(self):
        thread = threading.Thread(target=self.run)
        thread.start()
        try:
            while not self.started:
                time.sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            thread.join()


def get_threaded_uvicorn(config: uvicorn.Config):
    return Server(config=config)

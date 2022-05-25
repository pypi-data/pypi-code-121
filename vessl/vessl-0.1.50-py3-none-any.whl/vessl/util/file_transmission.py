from concurrent.futures import wait
from time import time

from requests_futures.sessions import FuturesSession

from vessl.cli._util import sizeof_fmt
from vessl.util.constant import PARALLEL_WORKERS


class FileTransmissionTracker:
    def __init__(self, total_count, total_size, action):
        self.start_time = time()
        self.total_count = total_count
        self.done_count = 0
        self.total_size = total_size
        self.done_size = 0
        self.last_printed_time = None
        self.action = action

    def increase_done_size(self, size: int):
        self.done_size += size

    def increase_done_count(self):
        self.done_count += 1

    def print_progress(self, force=False):
        if not self.last_printed_time:
            self.last_printed_time = time()

        elif force or time() - self.last_printed_time > 1:
            print(f"{sizeof_fmt(self.done_size)}/{sizeof_fmt(self.total_size)} "
                  f"({int(self.done_size/self.total_size*100)}%) {self.action}ed.")
            self.last_printed_time = time()

    def print_result(self):
        self.print_progress(force=True)
        print("Successfully {}ed {} out of {} file(s) in {} seconds".format(
            self.action,
            self.done_count,
            self.total_count,
            "%.2f" % (time() - self.start_time),
            ))


class FileTransmissionHandler:
    def __init__(self, future_func, action: str = "download", quiet: bool = False):
        self.session = FuturesSession(max_workers=PARALLEL_WORKERS)
        self.files = []
        self.total_count = 0
        self.total_size = 0
        self.quiet = quiet
        self.action = action
        self.future_func = future_func  # future_func(session, path, url, tracker) -> Future

    def add_file(self, full_path, url, size):
        self.total_count += 1
        self.total_size += size
        self.files.append((full_path, url))

    def run(self):
        tracker = None
        if not self.quiet:
            tracker = self._tracker()

        wait([self.future_func(self.session, full_path, url, tracker) for full_path, url in self.files])
        if tracker:
            tracker.print_result()

    def _tracker(self):
        return FileTransmissionTracker(self.total_count, self.total_size, self.action)

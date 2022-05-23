# Copyright 2020-2022 Daniel Harding
# Distributed as part of the pyflame project under the terms of the MIT license

import threading
import sys

from collections import defaultdict

from pyflame.stack import pack_stack


class Sampler:
    def __init__(self, sample_interval):
        self.sample_interval = sample_interval
        self.stack_counts = defaultdict(int)
        self.stop_event = threading.Event()
        self.thread = threading.Thread(
            target=_run_sample_thread,
            args=(
                threading.get_ident(),
                self.stack_counts,
                self.stop_event,
                sample_interval,
            ),
            name='pyflame sample thread',
        )
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.thread.join()
        return self.stack_counts


def _run_sample_thread(target_thread_id, stack_counts, stop_event, interval):
    _current_frames = sys._current_frames
    _pack_stack = pack_stack
    _stop_event_wait = stop_event.wait
    while True:
        try:
            frame = _current_frames().get(target_thread_id)
            if frame is None:
                break
            stack = _pack_stack(frame)
        finally:
            frame = None

        stack_counts[stack] += 1
        if _stop_event_wait(timeout=interval):
            break

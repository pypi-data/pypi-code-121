#!/usr/bin/env python3

# standards
from threading import Thread
from time import sleep

# hublot
from hublot.decorator import SCRAPER_LOCAL, ThreadLocalStackFrame


def thread_body(value: bool):
    num_sweeps = 50
    for _ in range(num_sweeps):
        SCRAPER_LOCAL.stack.append(ThreadLocalStackFrame(is_retry=value))
        sleep(0.01)
    for _ in range(num_sweeps):
        assert SCRAPER_LOCAL.stack.pop().is_retry is value
        sleep(0.01)


def test_thread_local_data():
    thread_a = Thread(target=thread_body, args=(True,))
    thread_b = Thread(target=thread_body, args=(False,))
    thread_a.start()
    thread_b.start()
    thread_a.join()
    thread_b.join()

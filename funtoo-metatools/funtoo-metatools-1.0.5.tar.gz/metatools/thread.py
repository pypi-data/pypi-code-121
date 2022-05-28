#!/usr/bin/env python3

from concurrent.futures.thread import ThreadPoolExecutor
from multiprocessing import cpu_count


def get_threadpool():
	return ThreadPoolExecutor(max_workers=cpu_count())




# vim: ts=4 sw=4 noet

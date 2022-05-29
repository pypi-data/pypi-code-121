"""Map-Reduce utils."""

import concurrent.futures

DEFAULT_MAX_THREADS = 4


def _run_parallel(workers, max_threads=DEFAULT_MAX_THREADS):
    """Run workers in parallel."""
    with concurrent.futures.ThreadPoolExecutor(max_threads) as thread_pool:
        future_list = []
        for worker in workers:
            future = thread_pool.submit(worker)
            future_list.append(future)

        for future in future_list:
            future.done()

        output_list = []
        for future in future_list:
            output_list.append(future.result())
        return output_list


def map_parallel(func_map, params_list, max_threads=DEFAULT_MAX_THREADS):
    """Run list(map(...)) in parallel.

    Args:
        func_map (function): Mapper function
        params_list (list): Params to be mapped
        max_threads (int, optional): Maximum parallel threads.
            DEFAULT_MAX_THREADS = 4

    .. code-block:: python

        >>> from utils import mr
        >>> print(mr.map_parallel(lambda x: x ** 2, [1, 2, 3, 4]))
        [1, 4, 9, 16]

    """

    def get_worker(params):
        def worker():
            return func_map(params)

        return worker

    workers = list(
        map(
            lambda params: get_worker(params=params),
            params_list,
        )
    )
    return _run_parallel(workers, max_threads)

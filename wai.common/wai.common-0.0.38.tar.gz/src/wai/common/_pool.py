"""
Provides utility functions for working with multiprocessing.Pool objects.
"""
from multiprocessing import Pool, Manager
from multiprocessing.managers import SyncManager
from multiprocessing.synchronize import Barrier
from typing import List, Any, Callable


def num_processes(pool: Pool) -> int:
    """
    Returns the number of sub-processes maintained by the given Pool.

    :param pool:    The pool.
    :return:        The number of sub-processes.
    """
    return pool._processes


def run_on_all(pool: Pool,
               func: Callable[[Any], Any],
               *args, **kwargs) -> List[Any]:
    """
    Runs a function on all processes managed by the given pool. Returns a list
    of results, one for each sub-process, with no guarantees as to order.

    :param pool:                The process pool.
    :param func:                The task to run.
    :param args:                The positional arguments to the task function.
    :param kwargs:              The keyword arguments to the task function.
    :return:                    The results from the workers.
    """
    # Get the number of processes to send the task too
    process_count: int = num_processes(pool)

    # Create a manager process to control a barrier for all workers
    barrier_manager: SyncManager = Manager()
    barrier: Barrier = barrier_manager.Barrier(process_count)

    # Create a copy of the task for each worker process with the barrier
    async_results = [pool.apply_async(func=run_with_barrier,
                                      args=(barrier, func, *args),
                                      kwds=kwargs)
                     for _ in range(process_count)]

    # Return the results when all are available
    return [async_result.get() for async_result in async_results]


def run_with_barrier(barrier: Barrier,
                     func: Callable[[Any], Any],
                     *args, **kwargs) -> Any:
    """
    Runs the given function with the provided arguments, once
    a barrier has been passed.

    :param barrier:     The barrier to pass before running.
    :param func:        The function to run.
    :param args:        The positional arguments to the function.
    :param kwargs:      The keyword arguments to the function.
    :return:            The result of running the function.
    """
    # Pass the barrier first
    barrier.wait()

    # Run the function
    return func(*args, **kwargs)

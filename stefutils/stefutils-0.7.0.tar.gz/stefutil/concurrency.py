"""
concurrency

intended for (potentially heavy) data processing
"""

import os
import concurrent.futures
from typing import List, Tuple, Dict, Iterable, Callable, TypeVar, Union

import numpy as np
from tqdm.std import tqdm as std_tqdm  # root for type check
from tqdm.auto import tqdm
from tqdm.contrib import concurrent as tqdm_concurrent

from stefutil.check_args import ca


__all__ = ['conc_map', 'batched_conc_map']


T = TypeVar('T')
K = TypeVar('K')

MapFn = Callable[[T], K]
BatchedMapFn = Callable[[Tuple[List[T], int, int]], List[K]]


def conc_map(
        fn: MapFn, it: Iterable[T], with_tqdm: Union[bool, Dict] = False, n_worker: int = os.cpu_count(), mode: str = 'thread'
) -> Iterable[K]:
    """
    Wrapper for `concurrent.futures.map`

    :param fn: A function
    :param it: A list of elements
    :param with_tqdm: If true, progress bar is shown
        If dict, treated as `tqdm` concurrent kwargs  # FYT `chunksize` is helpful
    :param n_worker: Number of concurrent workers
    :param mode: One of ['thread', 'process']
        Function has to be pickleable if 'process'
    :return: Iterator of `lst` elements mapped by `fn` with thread concurrency
    """
    ca.check_mismatch('Concurrency Mode', mode, ['thread', 'process'])
    if with_tqdm:
        cls = tqdm_concurrent.thread_map if mode == 'thread' else tqdm_concurrent.process_map
        args = (isinstance(with_tqdm, dict) and with_tqdm) or dict()
        return cls(fn, it, max_workers=n_worker, **args)
    else:
        cls = concurrent.futures.ThreadPoolExecutor if mode == 'thread' else concurrent.futures.ProcessPoolExecutor
        with cls(max_workers=n_worker) as executor:
            return executor.map(fn, it)


"""
classes instead of nested functions, pickleable for multiprocessing
"""


class Map:
    def __init__(self, fn, pbar=None):
        self.fn = fn
        self.pbar = pbar

    def __call__(self, x):
        ret = self.fn(x)
        if self.pbar:
            self.pbar.update(1)
        return ret


class BatchedMap:
    def __init__(self, fn, is_batched_fn: bool, pbar=None):
        self.fn = fn if is_batched_fn else Map(fn, pbar)
        self.pbar = pbar
        self.is_batched_fn = is_batched_fn

    def __call__(self, args):
        # adhere to single-argument signature for `conc_map`
        lst, s, e = args
        if self.is_batched_fn:
            ret = self.fn(lst[s:e])
            if self.pbar:
                # TODO: update on the element level may not give a good estimate of completion if too large a batch
                self.pbar.update(e-s + 1)
            return ret
        else:
            return [self.fn(lst[i]) for i in range(s, e)]


def batched_conc_map(
        fn: Union[MapFn, BatchedMapFn],
        it: Union[Iterable[T], List[T], np.array], n: int = None, n_worker: int = os.cpu_count(),
        batch_size: int = None,
        with_tqdm: Union[bool, dict, tqdm] = False,
        is_batched_fn: bool = False,
        mode: str = 'thread'
) -> List[K]:
    """
    Batched concurrent mapping, map elements in list in batches
    Operates on batch/subset of `lst` elements given inclusive begin & exclusive end indices

    :param fn: A map function that operates on a single element
    :param it: A list of elements to map
    :param n: #elements to map if `it` is not Sized
    :param n_worker: Number of concurrent workers
    :param batch_size: Number of elements for each sub-process worker
        Inferred based on number of workers if not given
    :param with_tqdm: If true, progress bar is shown
        progress is shown on an element-level if possible
    :param is_batched_fn: If true, `conc_map` is called on the function passed in,
        otherwise, A batched version is created internally
    :param mode: One of ['thread', 'process']

    .. note:: Concurrently is not invoked if too little list elements given number of workers
        Force concurrency with `batch_size`
    """
    n = n or len(it)
    if (n_worker > 1 and n > n_worker * 4) or batch_size:  # factor of 4 is arbitrary, otherwise not worse the overhead
        preprocess_batch = batch_size or round(n / n_worker / 2)
        strts: List[int] = list(range(0, n, preprocess_batch))
        ends: List[int] = strts[1:] + [n]  # inclusive begin, exclusive end
        lst_out = []

        pbar = None
        if with_tqdm:
            tqdm_args = dict(mode=mode, n_worker=n_worker)
            if mode == 'thread':  # Able to show progress on element level
                # so create such a progress bar & disable for `conc_map`
                tqdm_args['with_tqdm'] = False
                if isinstance(with_tqdm, bool):
                    pbar = tqdm(total=n)
                elif isinstance(with_tqdm, dict):
                    _args = dict(total=n)
                    _args.update(with_tqdm)
                    pbar = tqdm(**_args)
                else:
                    assert isinstance(with_tqdm, std_tqdm)
                    pbar = with_tqdm
            else:  # `process`, have to rely on `tqdm.concurrent` which shows progress on batch level, see `conc_map`
                tqdm_args['with_tqdm'] = with_tqdm
        else:
            tqdm_args = dict(with_tqdm=False)

        batched_map = BatchedMap(fn, is_batched_fn, pbar)
        map_out = conc_map(fn=batched_map, it=[(it, s, e) for s, e in zip(strts, ends)], **tqdm_args)
        for lst_ in map_out:
            lst_out.extend(lst_)
        return lst_out
    else:
        gen = tqdm(it) if with_tqdm else it
        if is_batched_fn:
            args = gen, 0, n
            return fn(*args)
        else:
            return [fn(x) for x in gen]

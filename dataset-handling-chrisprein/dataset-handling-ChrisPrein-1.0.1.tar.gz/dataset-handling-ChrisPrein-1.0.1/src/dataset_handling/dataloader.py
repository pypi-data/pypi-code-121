from abc import ABC, abstractmethod
from typing import Optional, Sequence, TypeVar, List, Generic, Iterator
from datetime import timedelta, datetime
from enum import Enum
import torch.utils.data.dataloader as to

TSample = TypeVar('TSample')

class DataLoader(to.DataLoader[TSample]):
    def __init__(self, dataset: to.Dataset[to.T_co], batch_size: Optional[int] = 1,
                 shuffle: bool = False, sampler: Optional[to.Sampler[int]] = None,
                 batch_sampler: Optional[to.Sampler[Sequence[int]]] = None,
                 num_workers: int = 0, collate_fn: to._collate_fn_t = lambda batch: batch,
                 pin_memory: bool = False, drop_last: bool = False,
                 timeout: float = 0, worker_init_fn: to._worker_init_fn_t = None,
                 multiprocessing_context=None, generator=None,
                 *, prefetch_factor: int = 2,
                 persistent_workers: bool = False):
        super().__init__(dataset=dataset, batch_size=batch_size, shuffle=shuffle, sampler=sampler, 
                    batch_sampler=batch_sampler, num_workers=num_workers, collate_fn=collate_fn, 
                    pin_memory=pin_memory, drop_last=drop_last, timeout=timeout, worker_init_fn=worker_init_fn, 
                    multiprocessing_context=multiprocessing_context, generator=generator, 
                    prefetch_factor=prefetch_factor, persistent_workers=persistent_workers)

    def __iter__(self) -> Iterator[TSample]:
        return super().__iter__()
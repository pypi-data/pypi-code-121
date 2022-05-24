# -*- coding: utf-8 -*-

from __future__ import annotations

import abc
import itertools
import warnings
from collections.abc import Callable, Iterable, Sequence
from typing import Any, Optional, TypeVar, Union, cast

import ignite.distributed as idist
import torch
from ignite.distributed.auto import DistributedProxySampler
from torch.utils.data import BatchSampler, DataLoader, Dataset
from torch.utils.data import IterableDataset as _IterableDataset
from torch.utils.data.dataset import IterableDataset
from torch.utils.data.sampler import RandomSampler, Sampler, SequentialSampler

from torchlight.utils.phase import ModeKeys, PhaseMixin


class Collator(PhaseMixin, metaclass=abc.ABCMeta):
    T = TypeVar("T", bound="Collator")

    def __init__(self, mode: ModeKeys = ModeKeys.TRAIN) -> None:
        self.mode = mode

    def __call__(self, batch: Sequence) -> Any:
        return self.collate_fn(batch)

    def encode(self, example) -> Any:  # pylint: disable=no-self-use
        return example

    def encode_batch(self, batch: Sequence) -> list:
        return list(map(self.encode, batch))

    def collate_train(self, batch: Sequence) -> Any:
        raise NotImplementedError()

    def collate_eval(self, batch: Sequence) -> Any:
        return self.collate_train(batch)

    def collate_predict(self, batch: Sequence) -> Any:
        return self.collate_train(batch)

    def _get_collate_fn(self):
        return {
            ModeKeys.TRAIN: self.collate_train,
            ModeKeys.EVAL: self.collate_eval,
            ModeKeys.PREDICT: self.collate_predict,
        }[self.mode]

    def _collate(self, encoded_batch):
        return self._get_collate_fn()(encoded_batch)

    def collate_fn(self, batch: Sequence) -> Any:
        encoded_batch = self.encode_batch(batch)
        collated = self._collate(encoded_batch)

        return collated


def _identity(x):
    return x


def _random_access_bucket(
    bucket: list, batch_size: int, drop_last: Optional[bool] = None
) -> Iterable:
    while bucket:
        size = len(bucket)
        if size <= batch_size:
            if size == batch_size or drop_last is False:
                yield bucket
            bucket = []
        else:
            # NOTE: Use `torch.randint` becasue
            # `DistributedProxySampler` use `torch.manual_seed`.
            start = cast(int, torch.randint(0, size - batch_size, size=(1,)).item())
            end = start + batch_size
            yield bucket[start:end]
            bucket = bucket[:start] + bucket[end:]


class BucketBatchSampler(BatchSampler):
    def __init__(
        self,
        dataset: Dataset,
        sampler: Sampler,
        batch_size: int,
        drop_last: bool,
        sort_key: Callable = _identity,
        batch_size_multiplier: int = 100,
    ) -> None:
        super().__init__(sampler, batch_size, drop_last)

        self.dataset = dataset
        self.bucket_size = min(
            batch_size_multiplier * batch_size, len(sampler)  # type: ignore
        )
        self.batch_sampler = BatchSampler(sampler, self.bucket_size, False)
        self.sort_key = sort_key

    def __iter__(self):
        for bucket in self.batch_sampler:
            bucket.sort(key=lambda i: self.sort_key(self.dataset[i]))

            yield from _random_access_bucket(bucket, self.batch_size, self.drop_last)


def bucket_batch_sampler(
    dataset: Dataset,
    batch_size: int,
    drop_last: bool,
    sort_key: Callable = _identity,
    batch_size_multiplier: int = 100,
) -> DistributedProxySampler:
    return DistributedProxySampler(
        BucketBatchSampler(
            dataset,
            RandomSampler(range(len(dataset))),  # type: ignore
            batch_size,
            drop_last,
            sort_key=sort_key,
            batch_size_multiplier=batch_size_multiplier,
        ),
        num_replicas=idist.get_world_size(),
        rank=idist.get_rank(),
    )


class IterableDataset(_IterableDataset):
    def __init__(
        self,
        generating_function: Callable,
        batch_size: int,
        world_size: Optional[int] = None,
        rank: Optional[int] = None,
        mode: ModeKeys = ModeKeys.TRAIN,  # TODO: Make wrapper.
    ) -> None:
        super().__init__()
        self.generating_function = generating_function
        self.batch_size = batch_size
        if ((rank is None) + (world_size is None)) % 2 != 0:
            raise ValueError("`rank` and `world_size` must both given or unspecified")
        self.world_size = world_size
        self.rank = rank
        self.mode = mode

    def _get_iterator(self):
        # Generate new iterator.
        iterator = self.generating_function()

        # Deal with `DistributedDataParallel`.
        if self.world_size is not None and self.rank is not None:
            iterator = itertools.islice(iterator, self.rank, None, self.world_size)

        # Deal with `num_workers` > 1 of `DataLoader`.
        worker_info = torch.utils.data.get_worker_info()
        if worker_info is not None:
            iterator = itertools.islice(
                iterator, worker_info.id, None, worker_info.num_workers
            )

        return iterator

    def __getitem__(self, index):
        raise RuntimeError("`IterableDataset` does not support indexing")

    def __iter__(self):
        yield from self._get_iterator()


class BucketIterableDataset(IterableDataset):
    def __init__(
        self,
        generating_function: Callable,
        batch_size: int,
        world_size: Optional[int] = None,
        rank: Optional[int] = None,
        sort_key: Callable = _identity,
        batch_size_multiplier: int = 100,
        mode: ModeKeys = ModeKeys.TRAIN,  # TODO: Make wrapper.
    ) -> None:
        super().__init__(
            generating_function, batch_size, world_size=world_size, rank=rank, mode=mode
        )
        self.bucket_size = batch_size_multiplier * batch_size
        self.sort_key = sort_key

    def __iter__(self):
        iterator = self._get_iterator()

        while bucket := list(itertools.islice(iterator, None, self.bucket_size)):
            bucket.sort(key=self.sort_key)

            for batch in _random_access_bucket(bucket, self.batch_size, False):
                yield from batch


def get_sampler(
    dataset: Dataset, train: bool
) -> Union[RandomSampler, SequentialSampler]:
    if train:
        sampler = RandomSampler(dataset)  # type: ignore
    else:
        sampler = SequentialSampler(dataset)  # type: ignore

    return sampler


def get_dataloader(
    dataset: Dataset,
    collate_fn: Optional[Union[Callable, Collator]] = None,
    sampler: Optional[Sampler] = None,
    batch_sampler: Optional[Sampler] = None,
    sort_key: Optional[Callable] = None,
    shuffle: bool = False,
    **kwargs,
) -> DataLoader:
    if not isinstance(dataset, IterableDataset):
        if batch_sampler is None:
            if sort_key is not None:
                if isinstance(collate_fn, Collator) and collate_fn.is_train():
                    warnings.warn(
                        "`sort_key` is given when `collate_fn.is_train()` is False"
                    )

                batch_sampler = bucket_batch_sampler(
                    dataset,  # type: ignore
                    kwargs["batch_size"],
                    drop_last=False,
                    sort_key=sort_key,
                )

                # When `batch_sampler` is given, `batch_size` must be 1
                # when initializing `DataLoader`.
                kwargs["batch_size"] = 1
                kwargs["batch_sampler"] = batch_sampler

            elif sampler is None:
                # `sampler` will be wrapped in `idist.auto_dataloader`,
                # so we dont' need `batch_sampler`.
                sampler = get_sampler(
                    dataset,
                    collate_fn.is_train()
                    if isinstance(collate_fn, Collator)
                    else shuffle,
                )

    kwargs.update(
        {
            "collate_fn": collate_fn,
            "sampler": sampler,
        }
    )

    dataloader = idist.auto_dataloader(dataset, **kwargs)  # type: DataLoader[Dataset]

    return dataloader

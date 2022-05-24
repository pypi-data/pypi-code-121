# -*- coding: utf-8 -*-

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from typing import Optional, Union

import torch
import torch.nn.functional as F


def split_tensors(
    tensors: Iterable[torch.Tensor], chunk_size: int, dim: int = 0
) -> list[tuple[torch.Tensor, ...]]:
    sizes = [t.size() for t in tensors]
    if not sizes:
        raise ValueError("At least one tensor must be given.")

    for prev, this in zip(sizes, sizes[1:]):
        if prev[dim] != this[dim]:
            raise ValueError(
                f"Size of dimension `dim` = {dim}"  # type: ignore
                " must be same for all input tensors, "
                f"got: {list(map(tuple, sizes))}."
            )

    splits = list(zip(*(torch.split(x, chunk_size, dim=dim) for x in tensors)))

    return splits


def split_apply(
    f: Callable,
    inputs: Iterable[torch.Tensor],
    chunk_size: int,
    *args,
    dim: int = 0,
    **kwargs,
) -> Union[torch.Tensor, tuple[torch.Tensor, ...]]:
    chunks = split_tensors(inputs, chunk_size=chunk_size, dim=dim)
    outputs = [f(*chunk, *args, **kwargs) for chunk in chunks]

    if all(isinstance(t, torch.Tensor) for t in outputs):
        return torch.cat(outputs, dim=dim)

    outputs = list(zip(*outputs))
    tuple_outputs = tuple(torch.cat(x, dim=dim) for x in outputs)

    return tuple_outputs


def check_tensors_dimension(tensors: Iterable[torch.Tensor], dim: int):
    if any(not isinstance(x, torch.Tensor) or x.ndim != dim for x in tensors):
        raise ValueError(f"`tensors` must be {dim}d tensors.")


def pad_stack_1d(
    tensors: Sequence[torch.Tensor],
    max_length: Optional[int] = None,
    return_lengths: bool = False,
) -> Union[torch.Tensor, tuple[torch.Tensor, torch.Tensor]]:
    # NOTE: Works for 1d tensors with size 0.

    check_tensors_dimension(tensors, 1)

    if max_length is None:
        length = torch.tensor([len(x) for x in tensors], dtype=torch.int64)
        max_length = max(length)
    else:
        if return_lengths:
            raise ValueError(
                "`return_lengths` must be False when `max_length` is given"
            )

    tensor = torch.stack([F.pad(x, [0, max_length - len(x)]) for x in tensors])

    if return_lengths:
        return tensor, length

    return tensor


def pad_stack_2d(
    tensors: Sequence[torch.Tensor], max_rows: int, max_columns: int
) -> torch.Tensor:
    # NOTE: Works for 2d tensors with size 0.

    check_tensors_dimension(tensors, 2)

    # https://discuss.pytorch.org/t/padding-zero-size-tensors/118777
    if max_rows == 0:
        return tensors[0].new_zeros(len(tensors), max_rows, max_columns)

    return torch.stack(
        [
            torch.nn.functional.pad(
                x, [0, max_columns - x.size(1), 0, max_rows - x.size(0)]
            )
            for x in tensors
        ]
    )

# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Optional, Union

import torch


def create_span_mask(
    starts: Union[list[int], torch.Tensor],
    ends: Union[list[int], torch.Tensor],
    length: int,
    dtype: torch.dtype = torch.int64,
    device: torch.device = torch.device("cpu"),
) -> torch.Tensor:
    if len(starts) != len(ends):
        raise ValueError(
            f"`start` and `end` should have same lengths: {len(starts)} != {len(ends)}"
        )

    if len(starts) == 0:
        return torch.zeros((0, length), dtype=dtype, device=device)

    def _convert_tensor(t, name):
        if isinstance(t, torch.Tensor):
            if t.ndim != 1:
                raise ValueError(
                    f"`{name}` must be 1d if passed as tensor, got ndim == {t.ndim}"
                )

            return t.clone().detach()

        return torch.tensor(t, dtype=dtype, device=device)

    start, end = _convert_tensor(starts, "starts"), _convert_tensor(ends, "ends")

    mask = torch.arange(length, dtype=dtype, device=device)
    mask = (start[:, None] <= mask) & (mask < end[:, None])
    mask = mask.type_as(start)

    return mask


def length_to_mask(
    length: torch.Tensor,
    max_len: Optional[Union[int, torch.Tensor]] = None,
    batch_first: bool = False,
    dtype: torch.dtype = torch.int64,
    device: Optional[torch.device] = None,
) -> torch.Tensor:
    if max_len is None:
        max_len = length.max()

    if device is None:
        device = length.device

    mask = torch.arange(max_len, device=device).unsqueeze(dim=1).expand(
        max_len, len(length)
    ) < length.unsqueeze(dim=0)
    mask = mask.type(dtype)

    return mask.transpose(0, 1) if batch_first else mask


def mask_to_length(
    mask: torch.Tensor,
    batch_first: bool = False,
    dtype: torch.dtype = torch.int64,
    device: Optional[torch.device] = None,
) -> torch.Tensor:
    length = mask.sum(dim=int(batch_first)).type(dtype)
    if device is not None:
        length = length.to(device)

    return length

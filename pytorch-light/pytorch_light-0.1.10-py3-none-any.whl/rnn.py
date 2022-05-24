# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Optional

import torch
import torch.nn as nn
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence


def get_rnn(cell: str) -> nn.Module:
    return globals()[cell.upper()]


def forward_rnn(
    encoder: nn.Module,
    input_: torch.Tensor,
    length: torch.Tensor,
    batch_first: bool = True,
    enforce_sorted: bool = False,
    padding_value: float = 0.0,
    total_length: Optional[int] = None,
) -> tuple:
    # ATM `length` must be 1d long tensor on CPU.
    # https://github.com/pytorch/pytorch/issues/43227
    packed = pack_padded_sequence(
        input_, length.cpu(), batch_first=batch_first, enforce_sorted=enforce_sorted
    )
    hidden, states = encoder(packed)
    hidden, _ = pad_packed_sequence(
        hidden,
        batch_first=batch_first,
        padding_value=padding_value,
        total_length=total_length,
    )

    return hidden, states


class RNN(nn.Module):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self.encoder = nn.RNN(*args, **kwargs)

    def forward(
        self,
        input_: torch.Tensor,
        length: torch.Tensor,
        batch_first: bool = True,
        enforce_sorted: bool = False,
        padding_value: float = 0.0,
        total_length: Optional[int] = None,
    ) -> tuple:
        return forward_rnn(
            self.encoder,
            input_,
            length,
            batch_first=batch_first,
            enforce_sorted=enforce_sorted,
            padding_value=padding_value,
            total_length=total_length,
        )


class GRU(nn.Module):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self.encoder = nn.GRU(*args, **kwargs)

    def forward(
        self,
        input_: torch.Tensor,
        length: torch.Tensor,
        batch_first: bool = True,
        enforce_sorted: bool = False,
        padding_value: float = 0.0,
        total_length: Optional[int] = None,
    ) -> tuple:
        return forward_rnn(
            self.encoder,
            input_,
            length,
            batch_first=batch_first,
            enforce_sorted=enforce_sorted,
            padding_value=padding_value,
            total_length=total_length,
        )


class LSTM(nn.Module):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self.encoder = nn.LSTM(*args, **kwargs)

    def forward(
        self,
        input_: torch.Tensor,
        length: torch.Tensor,
        batch_first: bool = True,
        enforce_sorted: bool = False,
        padding_value: float = 0.0,
        total_length: Optional[int] = None,
    ) -> tuple:
        return forward_rnn(
            self.encoder,
            input_,
            length,
            batch_first=batch_first,
            enforce_sorted=enforce_sorted,
            padding_value=padding_value,
            total_length=total_length,
        )

from typing import Optional
from functools import wraps

from torch import Tensor
from torch.nn.functional import (
    nll_loss as _nll_loss,
    cross_entropy as _cross_entropy,
)

# FIXME: This is a temporary fix before we can implement custom functions
from torch.nn.functional import *

from nxml.univ.nn.functional import (
    accuracy as _accuracy,
)


__all__ = [
    "nll_loss",
    "cross_entropy",
    "accuracy",
]


# wrappers

@wraps(_nll_loss)
def nll_loss(
    input: Tensor,
    target: Tensor,
    weight: Optional[Tensor] = None,
    ignore_index: int = -100,
    reduction: str = "mean",
):
    return _nll_loss(input, target, weight, ignore_index=ignore_index, reduction=reduction)


@wraps(_cross_entropy)
def cross_entropy(
    input: Tensor,
    target: Tensor,
    weight: Optional[Tensor] = None,
    ignore_index: int = -100,
    reduction: str = "mean",
    label_smoothing: float = 0.0,
):
    return _cross_entropy(
        input, target, weight, ignore_index=ignore_index, reduction=reduction,
        label_smoothing=label_smoothing,
    )


@wraps(_accuracy)
def accuracy(
    input: Tensor,
    target: Tensor,
    topk: int = 1,
    ignore_index: int = -100,
    reduction: str = "mean",
):
    return _accuracy(input, target, topk=topk, ignore_index=ignore_index, reduction=reduction)


# TODO: Change wraps to real "docstrings" to support IDE hints.

from typing import Any, Optional
from functools import wraps

from jax import jit

from nxml.univ.nn.functional import (
    nll_loss as _nll_loss,
    cross_entropy as _cross_entropy,
    accuracy as _accuracy,
)

Array = Any


__all__ = [
    "nll_loss",
    "cross_entropy",
    "accuracy",
]


jit_nll_loss = jit(
    _nll_loss,
    static_argnames=("ignore_index", "reduction"),
)


@wraps(_nll_loss)
def nll_loss(
    input: Array,
    target: Array,
    weight: Optional[Array] = None,
    ignore_index: int = -100,
    reduction: str = "mean",
):
    return jit_nll_loss(input, target, weight, ignore_index=ignore_index, reduction=reduction)


jit_cross_entropy = jit(
    _cross_entropy,
    static_argnames=("ignore_index", "reduction", "label_smoothing"),
)


@wraps(_cross_entropy)
def cross_entropy(
    input: Array,
    target: Array,
    weight: Optional[Array] = None,
    ignore_index: int = -100,
    reduction: str = "mean",
    label_smoothing: float = 0.0,
):
    return jit_cross_entropy(
        input, target, weight, ignore_index=ignore_index, reduction=reduction,
        label_smoothing=label_smoothing,
    )


jit_accuracy = jit(
    _accuracy,
    static_argnames=("topk", "ignore_index", "reduction"),
)


@wraps(_accuracy)
def accuracy(
    input: Array,
    target: Array,
    topk: int = 1,
    ignore_index: int = -100,
    reduction: str = "mean",
):
    return jit_accuracy(input, target, topk=topk, ignore_index=ignore_index, reduction=reduction)


# TODO: Change wraps to real "docstrings" to support IDE hints.

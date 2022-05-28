
import torch

from typing import Callable


def _except(f: Callable, x: torch.Tensor, *dim):
    # apply f on all dimensions except those specified in dim
    result = x
    dimensions = [d for d in range(len(x.shape)) if d not in dim]

    return f(result, dim=dimensions)


def sum_except(x: torch.Tensor, *dim):
    """ Sum all dimensions of x except the ones specified in dim """
    return _except(torch.sum, x, *dim)


def sum_except_batch(x):
    """ Sum all dimensions of x except the batch dimension """
    return sum_except(x, 0)


def mean_except(x: torch.Tensor, *dim):
    """ See sum_except """
    return _except(torch.mean, x, *dim)


def mean_except_batch(x):
    """ See sum_except_batch """
    return mean_except(x, 0)

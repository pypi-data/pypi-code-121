from typing import Optional
from typing import Tuple
from typing import Union

import numpy as np
import torch
import torch.nn as nn

from enot.models.operations.operations_registry import GLOBAL_ACTIVATION_FUNCTION_REGISTRY
from enot.models.operations.operations_registry import reg_activation_class_decorator

__all__ = [
    'calculate_hidden_channels',
    'same_padding',
    'ConvBN',
    'DepthwiseConvBN',
    'Swish',
    'SkipConnection',
]


class ConvBN(nn.Module):

    def __init__(
            self,
            in_channels: int,
            out_channels: int,
            kernel_size: int = 3,
            stride: int = 1,
            # padding='SAME',
            padding: Optional[int] = None,
            bn: bool = True,
            groups: int = 1,
            affine: bool = True,
            track: bool = True,
            activation: Optional[str] = None,
    ):

        super().__init__()

        if padding is None:
            padding = (kernel_size - 1) // 2

        self.conv = nn.Conv2d(
            in_channels,
            out_channels,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
            groups=groups,
            bias=not bn,
        )
        # pylint: disable=invalid-name
        self.bn = None

        if bn:
            self.bn = nn.BatchNorm2d(out_channels, affine=affine, track_running_stats=track)
        # pylint: enable=invalid-name

        self.activation = GLOBAL_ACTIVATION_FUNCTION_REGISTRY[activation]() if activation is not None else None

    def forward(self, x):

        x = self.conv(x)

        if self.bn is not None:
            x = self.bn(x)

        if self.activation is not None:
            x = self.activation(x)

        return x


class DepthwiseConvBN(ConvBN):

    def __init__(
            self,
            in_channels: int,
            kernel_size: int = 3,
            stride: int = 1,
            # padding='SAME',
            padding: Optional[int] = None,
            bn: bool = True,
            affine: bool = True,
            track: bool = True,
            activation: Optional[str] = None,
    ):

        super().__init__(
            in_channels=in_channels,
            out_channels=in_channels,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
            bn=bn,
            affine=affine,
            track=track,
            activation=activation,
            groups=in_channels,
        )


class SkipConnection(nn.Module):
    def __init__(self, operation: nn.Module, downsample: Optional[nn.Module] = None):
        super().__init__()

        self.operation = operation
        self.downsample = downsample

    def forward(self, x: torch.Tensor):
        y = self.operation(x)

        if self.downsample is not None:
            x = self.downsample(x)

        return y + x


def calculate_hidden_channels(in_channels, hidden_channels, expand_ratio):
    if hidden_channels is not None and expand_ratio is not None:
        raise ValueError('Only one of hidden_channels or expand_ratio must be used')
    if expand_ratio is not None:
        hidden_channels = round(in_channels * expand_ratio)
    return hidden_channels


def same_padding(
        kernel_size: Union[int, Tuple[int, ...]],
        dilation: Union[int, Tuple[int, ...]] = 1,
) -> Union[int, Tuple[int, ...]]:
    """Implement padding 'SAME'. This is only here to avoid code de-synchronization."""
    if not isinstance(kernel_size, tuple):
        kernel_size = [kernel_size]

    if not isinstance(dilation, tuple):
        dilation = [dilation]

    if len(kernel_size) < len(dilation):
        raise ValueError('The length of kernel_size should be the same or greater than dilation.')

    kernel_size = np.array(kernel_size)
    dilation = np.array(dilation)

    if np.any(kernel_size % 2 != 1):
        raise ValueError('This only works correctly with odd kernel sizes')
    kernel_size += (kernel_size + 1) * (dilation - 1)
    return tuple((kernel_size - 1) // 2)


@reg_activation_class_decorator
class Swish(nn.Module):
    def __init__(self):
        super().__init__()
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        return x * self.sigmoid(x)

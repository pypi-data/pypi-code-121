from typing import Optional
from typing import Tuple
from typing import Union

import torch.nn as nn
from enot.latency import LatencyMixin
from enot.latency import conv_mac_count
from enot.models.operations.common_operations import same_padding
from enot.models.operations.operations_registry import GLOBAL_ACTIVATION_FUNCTION_REGISTRY
from enot.models.operations.operations_registry import register_searchable_op
from enot.utils.common import input_hw
from enot.utils.common import is_valid_for_skip_connection
from torch import Tensor

__all__ = [
    'SearchableConv2d',
    'SearchableFuseableSkipConv',
]


@register_searchable_op('Conv', {
    'k': ('kernel_size', int),
    'activation': ('activation', str),
})
class SearchableConv2d(nn.Module, LatencyMixin):
    """Sequence of (conv2d, [activation_function], batch_norm) layers.
    """
    def __init__(
            self,
            in_channels: int,
            out_channels: int,
            kernel_size: int = 3,
            stride: Union[int, Tuple[int, int]] = 1,
            padding: Optional[int] = None,
            activation: Optional[str] = 'relu',
            use_skip_connection: bool = True,
    ):
        """
        Parameters
        ----------
        in_channels : int
            Number of channels in the input tensor.
        out_channels : int
            Number of channels produced by the convolution.
        kernel_size : int
            Size of the convolving kernel. Default value: 3
        stride : Union[int, Tuple[int, int]]
            Stride of the convolution. Default value: 1
        padding : int, optional
            Padding added to both sides of the input. Default value: None (that means 'same')
        activation : str, optional
            Name for used activation function.

            This function must be registered in GLOBAL_ACTIVATION_FUNCTION_REGISTRY
            from enot.operations.operations_registry.

            If activation is None - there is no activation_function.

            Default value: 'relu'
        use_skip_connection: bool
            Add skip connection (y+=x) if this flag is True
            and output produced by convolution has the same shape as input.
            Default value: True
        """
        super().__init__()

        self.in_channels = in_channels
        self.out_channels = out_channels

        self.stride = stride
        if padding is None:
            padding = same_padding(kernel_size)

        # Save arguments that may be used for latency calculation
        self.kernel_size = kernel_size
        self.padding = padding
        # bias=False because of batch norm
        self.conv2d = nn.Conv2d(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
            bias=False,
        )
        self.activation_function = None
        if activation is not None:
            self.activation_function = GLOBAL_ACTIVATION_FUNCTION_REGISTRY[activation]()
        self.batch_norm = nn.BatchNorm2d(out_channels)

        self.use_skip_connection = use_skip_connection and is_valid_for_skip_connection(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            padding=padding,
            stride=stride,
        )

    def forward(self, x):
        """
        Perform (conv2d, [activation_function if not None], batch_norm) sequentially.

        Parameters
        ----------
        x: torch.Tensor

        Returns
        -------
        output: torch.Tensor
            Tensor with results of computation.
        """
        y = x
        y = self.conv2d(y)
        if self.activation_function is not None:
            y = self.activation_function(y)

        y = self.batch_norm(y)
        if self.use_skip_connection:
            y += x

        return y

    def latency_mmac(self, inputs: Tuple[Tensor, ...]):
        latency_value, _ = conv_mac_count(
            spatial_size=input_hw(inputs),
            kernel_size=self.kernel_size,
            stride=self.stride,
            padding=self.padding,
            in_channels=self.in_channels,
            out_channels=self.out_channels,
            calculate_in_millions=True
        )

        return latency_value


@register_searchable_op('conv1x1-skip')
class SearchableFuseableSkipConv(SearchableConv2d):
    """
    SearchableConv2d without activation function, and with kernel_size=1.
    Used for matching input and output channels of search blocks.
    """
    def __init__(
            self,
            in_channels: int,
            out_channels: int,
            stride: Union[int, Tuple[int, int]] = 1,
            use_skip_connection: bool = True,
    ):
        super().__init__(
            in_channels,
            out_channels,
            kernel_size=1,
            stride=stride,
            padding=None,
            activation=None,
            use_skip_connection=use_skip_connection,
        )

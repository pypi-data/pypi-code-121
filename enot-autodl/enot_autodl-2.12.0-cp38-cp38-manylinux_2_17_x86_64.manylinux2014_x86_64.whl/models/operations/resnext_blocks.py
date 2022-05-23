from typing import Optional
from typing import Tuple

import torch.nn as nn
from enot.latency import LatencyMixin
from enot.latency import conv_mac_count
from enot.models.operations.common_operations import ConvBN
from enot.models.operations.common_operations import calculate_hidden_channels
from enot.models.operations.common_operations import same_padding
from enot.models.operations.operations_registry import GLOBAL_ACTIVATION_FUNCTION_REGISTRY
from enot.models.operations.operations_registry import register_searchable_op
from enot.utils.common import input_hw
from enot.utils.common import is_valid_for_skip_connection
from torch import Tensor

__all__ = [
    'SearchableResNext',
]


_RNXT_ARG_DESCRIPTIONS = {
    'k': ('kernel_size', int),
    't': ('expand_ratio', float),
    'c': ('cardinality', int),
    'activation': ('activation', str),
}


@register_searchable_op('RNXT', _RNXT_ARG_DESCRIPTIONS)
class SearchableResNext(nn.Module, LatencyMixin):
    """
    ResNext block with group convolution.
    .. _original paper:
    https://arxiv.org/pdf/1611.05431.pdf, fig. 3(c)
    """
    def __init__(
            self,
            in_channels: int,
            out_channels: int,
            hidden_channels: Optional[int] = None,
            expand_ratio: Optional[float] = None,
            kernel_size: int = 3,
            cardinality: int = 8,
            stride: int = 1,
            padding: Optional[int] = None,
            activation: str = 'relu',
            use_skip_connection: bool = True,
    ):
        """
        Parameters
        ----------
        in_channels: int
            Number of channels in the input tensor.
        out_channels: int
            Number of channels of output tensor.
        hidden_channels: int, optional
            Number of channels in the convolution inside ResnetBlock.
            Only one of hidden_channels and expand_ratio con be set.
            If both is None - hidden_channels=in_channels // 2.
        expand_ratio: float, optional
            Used for computing hidden_channels.
            hidden_channels = round(in_channels * expand_ratio).
        kernel_size: int
            Kernel size for middle group convolution in the block.
        cardinality: int
            Number of groups for middle group convolution.
        stride: int
            Stride of the depthwise convolution. Default value: 1
        padding: int, optional
            Padding added to both sides of the input. Default value: None (that means 'same')
        activation: str, optional
            Name for used activation function.

            This function must be registered in GLOBAL_ACTIVATION_FUNCTION_REGISTRY
            from enot.operations.operations_registry.

            If activation is None - there is no activation_function.

            Default value: 'relu'
        """

        super().__init__()

        if padding is None:
            padding = same_padding(kernel_size)

        self.kernel_size = kernel_size
        self.cardinality = cardinality
        self.expand_ratio = expand_ratio
        self.stride = stride
        self.padding = padding
        self.in_channels = in_channels
        self.out_channels = out_channels

        hidden_channels = calculate_hidden_channels(out_channels, hidden_channels, expand_ratio)
        if hidden_channels is None:
            hidden_channels = out_channels // 2
        hidden_channels *= cardinality
        self.hidden_channels = hidden_channels

        activation_function = GLOBAL_ACTIVATION_FUNCTION_REGISTRY[activation]
        self.block_operations = nn.Sequential(
            ConvBN(in_channels, hidden_channels, 1),
            activation_function(),
            ConvBN(hidden_channels, hidden_channels, kernel_size, stride, padding, groups=cardinality),
            activation_function(),
            ConvBN(hidden_channels, out_channels, 1)
        )

        self.use_skip_connection = use_skip_connection and is_valid_for_skip_connection(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            padding=padding,
            stride=stride,
        )

    def forward(self, x):
        y = x
        y = self.block_operations(y)

        if self.use_skip_connection:
            y += x

        return y

    def latency_mmac(self, inputs: Tuple[Tensor, ...]):
        mac_expand_conv, spatial_size = conv_mac_count(
            spatial_size=input_hw(inputs),
            kernel_size=1,
            stride=1,
            in_channels=self.in_channels,
            out_channels=self.hidden_channels,
            calculate_in_millions=True,
        )
        mac_group_conv, spatial_size = conv_mac_count(
            spatial_size,
            kernel_size=self.kernel_size,
            stride=self.stride,
            padding=self.padding,
            in_channels=self.hidden_channels,
            out_channels=self.hidden_channels,
            groups=self.cardinality,
            calculate_in_millions=True,
        )
        mac_squeeze_conv, _ = conv_mac_count(
            spatial_size,
            kernel_size=1,
            stride=1,
            in_channels=self.hidden_channels,
            out_channels=self.out_channels,
            calculate_in_millions=True,
        )
        return mac_expand_conv + mac_group_conv + mac_squeeze_conv

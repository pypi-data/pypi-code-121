from typing import Optional
from typing import Tuple

import torch.nn as nn
from enot.latency import LatencyMixin
from enot.latency import rn_mac_count
from enot.models.operations.common_operations import ConvBN
from enot.models.operations.common_operations import calculate_hidden_channels
from enot.models.operations.common_operations import same_padding
from enot.models.operations.operations_registry import GLOBAL_ACTIVATION_FUNCTION_REGISTRY
from enot.models.operations.operations_registry import register_searchable_op
from enot.utils.common import input_hw
from enot.utils.common import is_valid_for_skip_connection
from torch import Tensor

__all__ = [
    'SearchableResNetD',
    'SearchableResNetE',
]


_RN_ARG_DESCRIPTIONS = {
    'k1': ('squeeze_kernel_size', int),
    'k2': ('expand_kernel_size', int),
    't': ('expand_ratio', float),
    'activation': ('activation', str),
}


@register_searchable_op('RN-D', _RN_ARG_DESCRIPTIONS)
class SearchableResNetD(nn.Module, LatencyMixin):
    """
    D type of ResNet block.
    .. _original paper:
    https://arxiv.org/pdf/1603.05027.pdf fig. 4(d)
    """
    def __init__(
            self,
            in_channels: int,
            out_channels: int,
            hidden_channels: Optional[int] = None,
            expand_ratio: Optional[float] = None,
            squeeze_kernel_size: int = 3,
            expand_kernel_size: int = 3,
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
        squeeze_kernel_size: int
            Kernel size for squeeze convolution from in_channels to hidden_channels.
        expand_kernel_size: int
            Kernel size for expand convolution from hidden_channels to out_channels.
        stride: int
            Stride of the depthwise convolution. Default value: 1
        padding: int, optional
            Padding added to both sides of the input. Default value: None (that means 'same')
        activation: str, optional
            Name for used activation function.

            This function must be registered in GLOBAL_ACTIVATION_FUNCTION_REGISTRY
            from enot.operations.operations_registry.

            If activation is None - there is no activation_function

            Default value: 'relu'
        use_skip_connection: bool
            Add skip connection (y+=x) if this flag is True, in_channels==out_channels and stride==1.
            Default value: True
        """
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels

        if padding is None:
            padding = same_padding(squeeze_kernel_size)

        # Save arguments that may be used for latency calculation
        self.expand_ratio = expand_ratio
        self.expand_kernel_size = expand_kernel_size
        self.squeeze_kernel_size = squeeze_kernel_size
        self.stride = stride
        self.padding = padding

        hidden_channels = calculate_hidden_channels(in_channels, hidden_channels, expand_ratio)
        if hidden_channels is None:
            hidden_channels = in_channels // 2

        activation_function = GLOBAL_ACTIVATION_FUNCTION_REGISTRY[activation]
        self.block_operations = nn.Sequential(
            activation_function(),
            ConvBN(in_channels, hidden_channels, squeeze_kernel_size, stride, padding),
            activation_function(),
            ConvBN(hidden_channels, out_channels, expand_kernel_size),
        )

        self.use_skip_connection = use_skip_connection and is_valid_for_skip_connection(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=squeeze_kernel_size,
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
        return rn_mac_count(
            spatial_size=input_hw(inputs),
            squeeze_kernel_size=self.squeeze_kernel_size,
            expand_kernel_size=self.expand_kernel_size,
            expand_ratio=self.expand_ratio,
            stride=self.stride,
            in_channels=self.in_channels,
            out_channels=self.out_channels,
            padding=self.padding,
            calculate_in_millions=True
        )


@register_searchable_op('RN-E', _RN_ARG_DESCRIPTIONS)
class SearchableResNetE(nn.Module, LatencyMixin):
    """
    E type of ResNet block.
    .. _original paper:
    https://arxiv.org/pdf/1603.05027.pdf, fig. 4(e)
    """
    def __init__(
            self,
            in_channels: int,
            out_channels: int,
            hidden_channels: Optional[int] = None,
            expand_ratio: Optional[float] = None,
            squeeze_kernel_size: int = 3,
            expand_kernel_size: int = 3,
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
        squeeze_kernel_size: int
            Kernel size for squeeze convolution from in_channels to hidden_channels.
        expand_kernel_size: int
            Kernel size for expand convolution from hidden_channels to out_channels.
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
        use_skip_connection: bool
            Add skip connection (y+=x) if this flag is True
            and output produced by convolution has the same shape as input.
            Default value: True
        """
        super().__init__()

        self.in_channels = in_channels
        self.out_channels = out_channels
        if padding is None:
            padding = same_padding(squeeze_kernel_size)

        # Save arguments that may be used for latency calculation
        self.expand_ratio = expand_ratio
        self.expand_kernel_size = expand_kernel_size
        self.squeeze_kernel_size = squeeze_kernel_size
        self.stride = stride
        self.padding = padding

        hidden_channels = calculate_hidden_channels(in_channels, hidden_channels, expand_ratio)
        if hidden_channels is None:
            hidden_channels = in_channels // 2

        activation_function = GLOBAL_ACTIVATION_FUNCTION_REGISTRY[activation]
        self.block_operations = nn.Sequential(
            nn.BatchNorm2d(in_channels),
            activation_function(),
            ConvBN(in_channels, hidden_channels, squeeze_kernel_size, stride, padding),
            activation_function(),
            nn.Conv2d(hidden_channels, out_channels, expand_kernel_size, padding=same_padding(expand_kernel_size)),
            nn.BatchNorm2d(out_channels),
        )

        self.use_skip_connection = use_skip_connection and is_valid_for_skip_connection(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=squeeze_kernel_size,
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
        return rn_mac_count(
            spatial_size=input_hw(inputs),
            squeeze_kernel_size=self.squeeze_kernel_size,
            expand_kernel_size=self.expand_kernel_size,
            expand_ratio=self.expand_ratio,
            stride=self.stride,
            in_channels=self.in_channels,
            out_channels=self.out_channels,
            padding=self.padding,
            calculate_in_millions=True
        )

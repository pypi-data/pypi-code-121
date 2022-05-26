# Copyright 2021 The KaiJIN Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
r"""attention blocks
"""
import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd.function import once_differentiable

try:
  from tw import _C
except ImportError:
  _C = None

from .conv import _make_divisible

__all__ = [
    'CBAMModule',
    'CECAModule',
    'ChannelAttention',
    'CollectAttention',
    'DistributeAttention',
    'ECAModule',
    'EffectiveSEModule',
    'SEModule',
    'SpatialAttention',
    'SqueezeExciteModule',
]

#!<-----------------------------------------------------------------------------
#!< PSA Block
#!<-----------------------------------------------------------------------------


class _PSACollect(torch.autograd.Function):

  @staticmethod
  def forward(ctx, hc):
    out = _C.psa_forward(hc, 1)
    ctx.save_for_backward(hc)
    return out

  @staticmethod
  @once_differentiable
  def backward(ctx, dout):
    hc = ctx.saved_tensors
    dhc = _C.psa_backward(dout, hc[0], 1)
    return dhc


class _PSADistribute(torch.autograd.Function):

  @staticmethod
  def forward(ctx, hc):
    out = _C.psa_forward(hc, 2)
    ctx.save_for_backward(hc)
    return out

  @staticmethod
  @once_differentiable
  def backward(ctx, dout):
    hc = ctx.saved_tensors
    dhc = _C.psa_backward(dout, hc[0], 2)
    return dhc


psa_collect = _PSACollect.apply
psa_distribute = _PSADistribute.apply


class CollectAttention(nn.Module):
  """Collect Attention Generation Module"""

  def __init__(self):
    super(CollectAttention, self).__init__()

  def forward(self, x):
    out = psa_collect(x)
    return out


class DistributeAttention(nn.Module):
  """Distribute Attention Generation Module"""

  def __init__(self):
    super(DistributeAttention, self).__init__()

  def forward(self, x):
    out = psa_distribute(x)
    return out


#!<-----------------------------------------------------------------------------
#!< SE Block
#!<-----------------------------------------------------------------------------


class SEModule(nn.Module):
  """ SE Module as defined in original SE-Nets with a few additions

    An SE implementation originally based on PyTorch SE-Net impl.
    Has since evolved with additional functionality / configuration.

    Paper: `Squeeze-and-Excitation Networks` - https://arxiv.org/abs/1709.01507

    Additions include:
      - divisor can be specified to keep channels % div == 0 (default: 8)
      - reduction channels can be specified directly by arg (if rd_channels is set)
      - reduction channels can be specified by float rd_ratio (default: 1/16)
      - global max pooling can be added to the squeeze aggregation
      - customizable activation, normalization, and gate layer
  """

  def __init__(self, channels, rd_ratio=1. / 16, rd_channels=None, rd_divisor=8, add_maxpool=False,
               act_layer=nn.ReLU, norm_layer=None, gate_layer=torch.sigmoid):
    super(SEModule, self).__init__()
    self.add_maxpool = add_maxpool
    if not rd_channels:
      rd_channels = _make_divisible(channels * rd_ratio, rd_divisor, round_limit=0.)
    self.fc1 = nn.Conv2d(channels, rd_channels, kernel_size=1, bias=True)
    self.bn = norm_layer(rd_channels) if norm_layer else nn.Identity()
    self.act = act_layer()
    self.fc2 = nn.Conv2d(rd_channels, channels, kernel_size=1, bias=True)
    self.gate = gate_layer

  def forward(self, x):
    x_se = x.mean((2, 3), keepdim=True)
    if self.add_maxpool:
      # experimental codepath, may remove or change
      x_se = 0.5 * x_se + 0.5 * x.amax((2, 3), keepdim=True)
    x_se = self.fc1(x_se)
    x_se = self.act(self.bn(x_se))
    x_se = self.fc2(x_se)
    return x * self.gate(x_se)


class SqueezeExciteModule(nn.Module):
  """ Squeeze-and-Excitation w/ specific features for EfficientNet/MobileNet family

  Args:
      in_chs (int): input channels to layer
      rd_ratio (float): ratio of squeeze reduction
      act_layer (nn.Module): activation layer of containing block
      gate_layer (Callable): attention gate function
      force_act_layer (nn.Module): override block's activation fn if this is set/bound
      rd_round_fn (Callable): specify a fn to calculate rounding of reduced chs
  """

  def __init__(self, channels, rd_ratio=0.25, rd_channels=None, act_layer=nn.ReLU,
               force_act_layer=None, gate_layer=nn.Sigmoid, rd_round_fn=None):
    super(SqueezeExciteModule, self).__init__()
    if rd_channels is None:
      rd_round_fn = rd_round_fn or round
      rd_channels = rd_round_fn(channels * rd_ratio)
    act_layer = force_act_layer or act_layer
    self.conv_reduce = nn.Conv2d(channels, rd_channels, 1, bias=True)
    self.act1 = act_layer()
    self.conv_expand = nn.Conv2d(rd_channels, channels, 1, bias=True)
    self.gate = gate_layer()

  def forward(self, x):
    x_se = x.mean((2, 3), keepdim=True)
    x_se = self.conv_reduce(x_se)
    x_se = self.act1(x_se)
    x_se = self.conv_expand(x_se)
    return x * self.gate(x_se)


class EffectiveSEModule(nn.Module):
  """ 'Effective Squeeze-Excitation
    From `CenterMask : Real-Time Anchor-Free Instance Segmentation`
      - https://arxiv.org/abs/1911.06667
  """

  def __init__(self, channels, add_maxpool=False, gate_layer='hard_sigmoid', **_):
    super(EffectiveSEModule, self).__init__()
    self.add_maxpool = add_maxpool
    self.fc = nn.Conv2d(channels, channels, kernel_size=1, padding=0)
    self.gate = create_act_layer(gate_layer)

  def forward(self, x):
    x_se = x.mean((2, 3), keepdim=True)
    if self.add_maxpool:
      # experimental codepath, may remove or change
      x_se = 0.5 * x_se + 0.5 * x.amax((2, 3), keepdim=True)
    x_se = self.fc(x_se)
    return x * self.gate(x_se)


#!<-----------------------------------------------------------------------------
#!< ECA Block
#!<-----------------------------------------------------------------------------

class ECAModule(nn.Module):
  """Constructs an ECA module.

  Args:
      channels: Number of channels of the input feature map for use in adaptive kernel sizes
          for actual calculations according to channel.
          gamma, beta: when channel is given parameters of mapping function
          refer to original paper https://arxiv.org/pdf/1910.03151.pdf
          (default=None. if channel size not given, use k_size given for kernel size.)
      kernel_size: Adaptive selection of kernel size (default=3)
      gamm: used in kernel_size calc, see above
      beta: used in kernel_size calc, see above
      act_layer: optional non-linearity after conv, enables conv bias, this is an experiment
      gate_layer: gating non-linearity to use
  """

  def __init__(self, channels=None, kernel_size=3, gamma=2, beta=1, act_layer=None, gate_layer=torch.sigmoid,
               rd_ratio=1 / 8, rd_channels=None, rd_divisor=8, use_mlp=False):
    super(ECAModule, self).__init__()
    if channels is not None:
      t = int(abs(math.log(channels, 2) + beta) / gamma)
      kernel_size = max(t if t % 2 else t + 1, 3)
    assert kernel_size % 2 == 1
    padding = (kernel_size - 1) // 2
    self.conv = nn.Conv1d(1, 1, kernel_size=kernel_size, padding=padding, bias=False)
    self.act = None
    self.conv2 = None
    self.gate = gate_layer

  def forward(self, x):
    y = x.mean((2, 3)).view(x.shape[0], 1, -1)  # view for 1d conv
    y = self.conv(y)
    if self.conv2 is not None:
      y = self.act(y)
      y = self.conv2(y)
    y = self.gate(y).view(x.shape[0], -1, 1, 1)
    return x * y.expand_as(x)


class CECAModule(nn.Module):
  """Constructs a circular ECA module.

  ECA module where the conv uses circular padding rather than zero padding.
  Unlike the spatial dimension, the channels do not have inherent ordering nor
  locality. Although this module in essence, applies such an assumption, it is unnecessary
  to limit the channels on either "edge" from being circularly adapted to each other.
  This will fundamentally increase connectivity and possibly increase performance metrics
  (accuracy, robustness), without significantly impacting resource metrics
  (parameter size, throughput,latency, etc)

  Args:
      channels: Number of channels of the input feature map for use in adaptive kernel sizes
          for actual calculations according to channel.
          gamma, beta: when channel is given parameters of mapping function
          refer to original paper https://arxiv.org/pdf/1910.03151.pdf
          (default=None. if channel size not given, use k_size given for kernel size.)
      kernel_size: Adaptive selection of kernel size (default=3)
      gamm: used in kernel_size calc, see above
      beta: used in kernel_size calc, see above
      act_layer: optional non-linearity after conv, enables conv bias, this is an experiment
      gate_layer: gating non-linearity to use
  """

  def __init__(self, channels=None, kernel_size=3, gamma=2, beta=1, act_layer=None, gate_layer='sigmoid'):
    super(CECAModule, self).__init__()
    if channels is not None:
      t = int(abs(math.log(channels, 2) + beta) / gamma)
      kernel_size = max(t if t % 2 else t + 1, 3)
    has_act = act_layer is not None
    assert kernel_size % 2 == 1

    # PyTorch circular padding mode is buggy as of pytorch 1.4
    # see https://github.com/pytorch/pytorch/pull/17240
    # implement manual circular padding
    self.padding = (kernel_size - 1) // 2
    self.conv = nn.Conv1d(1, 1, kernel_size=kernel_size, padding=0, bias=has_act)
    self.gate = create_act_layer(gate_layer)

  def forward(self, x):
    y = x.mean((2, 3)).view(x.shape[0], 1, -1)
    # Manually implement circular padding, F.pad does not seemed to be bugged
    y = F.pad(y, (self.padding, self.padding), mode='circular')
    y = self.conv(y)
    y = self.gate(y).view(x.shape[0], -1, 1, 1)
    return x * y.expand_as(x)


#!<-----------------------------------------------------------------------------
#!< CBAM Attention
#!<-----------------------------------------------------------------------------


class ChannelAttention(nn.Module):
  """ Original CBAM channel attention module, currently avg + max pool variant only.
  """

  def __init__(
          self, channels, rd_ratio=1. / 16, rd_channels=None, rd_divisor=1,
          act_layer=nn.ReLU, gate_layer='sigmoid', mlp_bias=False):
    super(ChannelAttention, self).__init__()
    if not rd_channels:
      rd_channels = _make_divisible(channels * rd_ratio, rd_divisor, round_limit=0.)
    self.fc1 = nn.Conv2d(channels, rd_channels, 1, bias=mlp_bias)
    self.act = act_layer()
    self.fc2 = nn.Conv2d(rd_channels, channels, 1, bias=mlp_bias)
    self.gate = create_act_layer(gate_layer)

  def forward(self, x):
    x_avg = self.fc2(self.act(self.fc1(x.mean((2, 3), keepdim=True))))
    x_max = self.fc2(self.act(self.fc1(x.amax((2, 3), keepdim=True))))
    return x * self.gate(x_avg + x_max)


class SpatialAttention(nn.Module):
  """ Original CBAM spatial attention module
  """

  def __init__(self, kernel_size=7, gate_layer='sigmoid'):
    super(SpatialAttention, self).__init__()
    self.conv = ConvBnAct(2, 1, kernel_size, act_layer=None)
    self.gate = create_act_layer(gate_layer)

  def forward(self, x):
    x_attn = torch.cat([x.mean(dim=1, keepdim=True), x.amax(dim=1, keepdim=True)], dim=1)
    x_attn = self.conv(x_attn)
    return x * self.gate(x_attn)


class CBAMModule(nn.Module):
  """CBAM: Convolutional Block Attention Module: https://arxiv.org/abs/1807.06521
  """

  def __init__(self, channels, rd_ratio=1. / 16, rd_channels=None, rd_divisor=1,
               spatial_kernel_size=7, act_layer=nn.ReLU, gate_layer='sigmoid', mlp_bias=False):
    super(CBAMModule, self).__init__()
    self.channel = ChannelAttention(
        channels, rd_ratio=rd_ratio, rd_channels=rd_channels,
        rd_divisor=rd_divisor, act_layer=act_layer, gate_layer=gate_layer, mlp_bias=mlp_bias)
    self.spatial = SpatialAttention(spatial_kernel_size, gate_layer=gate_layer)

  def forward(self, x):
    x = self.channel(x)
    x = self.spatial(x)
    return x

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
import math
import functools
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from torch.autograd import Function
from torch.autograd.function import once_differentiable
from torch.nn.modules.utils import _pair

try:
  from tw import _C
except ImportError:
  _C = None

__all__ = [
    'CondConv2d',
    'CondConvResidual',
    'ConvBnAct',
    'ConvModule',
    'DeformConv',
    'DeformConvFunction',
    'DepthwiseSeparableConv',
    'EdgeResidual',
    'InvertedResidual',
    'MixedConv2d',
    'ModulatedDeformConv',
    'ModulatedDeformConvFunction',
    'ModulatedDeformConvPack',
    'SameConv2d',
]

#!<-----------------------------------------------------------------------------
#!< Tensorflow Same/Valid Padding Convolution
#!<-----------------------------------------------------------------------------


def _round_channels(channels, multiplier=1.0, divisor=8, channel_min=None, round_limit=0.9):
  """Round number of filters based on depth multiplier."""
  if not multiplier:
    return channels
  return _make_divisible(channels * multiplier, divisor, channel_min, round_limit=round_limit)


def _make_divisible(v, divisor=8, min_value=None, round_limit=.9):
  min_value = min_value or divisor
  new_v = max(min_value, int(v + divisor / 2) // divisor * divisor)
  # Make sure that round down does not go down by more than 10%.
  if new_v < round_limit * v:
    new_v += divisor
  return new_v


def _split_channels(num_chan, num_groups):
  split = [num_chan // num_groups for _ in range(num_groups)]
  split[0] += num_chan - sum(split)
  return split


def _get_padding(kernel_size: int, stride: int = 1, dilation: int = 1, **_) -> int:
  # Calculate symmetric padding for a convolution
  padding = ((stride - 1) + dilation * (kernel_size - 1)) // 2
  return padding


def _get_same_padding(x: int, k: int, s: int, d: int):
  # Calculate asymmetric TensorFlow-like 'SAME' padding for a convolution
  return max((math.ceil(x / s) - 1) * s + (k - 1) * d + 1 - x, 0)


def _same_padding(x, k, s, d, value=0.0):
  # dynamically pad input x with 'SAME' padding for conv with specified args
  ih, iw = x.size()[-2:]
  pad_h, pad_w = _get_same_padding(ih, k[0], s[0], d[0]), _get_same_padding(iw, k[1], s[1], d[1])
  if pad_h > 0 or pad_w > 0:
    x = F.pad(x, [pad_w // 2, pad_w - pad_w // 2, pad_h // 2, pad_h - pad_h // 2], value=value)
  return x


def _is_static_pad(kernel_size: int, stride: int = 1, dilation: int = 1, **_):
  # can same padding for given args be done statically?
  return stride == 1 and (dilation * (kernel_size - 1)) % 2 == 0


def _get_padding_value(padding, kernel_size, **kwargs):
  dynamic = False
  if isinstance(padding, str):
    # for any string padding, the padding will be calculated for you, one of three ways
    padding = padding.lower()
    if padding == 'same':
      # TF compatible 'SAME' padding, has a performance and GPU memory allocation impact
      if _is_static_pad(kernel_size, **kwargs):
        # static case, no extra overhead
        padding = _get_padding(kernel_size, **kwargs)
      else:
        # dynamic 'SAME' padding, has runtime/GPU memory overhead
        padding = 0
        dynamic = True
    elif padding == 'valid':
      # 'VALID' padding, same as padding=0
      padding = 0
    else:
      # Default to PyTorch style 'same'-ish symmetric padding
      padding = _get_padding(kernel_size, **kwargs)
  return padding, dynamic


def _conv2d_same(x, weight, bias=None, stride=(1, 1), padding=(0, 0), dilation=(1, 1), groups=1):
  x = _same_padding(x, weight.shape[-2:], stride, dilation)
  return F.conv2d(x, weight, bias, stride, (0, 0), dilation, groups)


class SameConv2d(nn.Conv2d):
  """ Tensorflow like 'SAME' convolution wrapper for 2D convolutions
  """

  def __init__(self, in_channels, out_channels, kernel_size, stride=1,
               padding=0, dilation=1, groups=1, bias=True):
    super(SameConv2d, self).__init__(in_channels, out_channels, kernel_size,
                                     stride, 0, dilation, groups, bias)

  def forward(self, x):
    return _conv2d_same(x, self.weight, self.bias, self.stride, self.padding,
                        self.dilation, self.groups)


def _create_conv2d_pad(in_chs, out_chs, kernel_size, **kwargs):
  """create a conv2d compatiable with tensorflow same padding.
  """
  padding = kwargs.pop('padding', '')
  kwargs.setdefault('bias', False)
  padding, is_dynamic = _get_padding_value(padding, kernel_size, **kwargs)
  if is_dynamic:
    return SameConv2d(in_chs, out_chs, kernel_size, **kwargs)
  else:
    return nn.Conv2d(in_chs, out_chs, kernel_size, padding=padding, **kwargs)


class MixedConv2d(nn.ModuleDict):
  """ Mixed Grouped Convolution

    Based on MDConv and GroupedConv in MixNet impl:
    https://github.com/tensorflow/tpu/blob/master/models/official/mnasnet/mixnet/custom_layers.py

    Paper: MixConv: Mixed Depthwise Convolutional Kernels
    (https://arxiv.org/abs/1907.09595)

  """

  def __init__(self, in_channels, out_channels, kernel_size=3,
               stride=1, padding='', dilation=1, depthwise=False, **kwargs):
    super(MixedConv2d, self).__init__()

    kernel_size = kernel_size if isinstance(kernel_size, list) else [kernel_size]
    num_groups = len(kernel_size)
    in_splits = _split_channels(in_channels, num_groups)
    out_splits = _split_channels(out_channels, num_groups)
    self.in_channels = sum(in_splits)
    self.out_channels = sum(out_splits)
    for idx, (k, in_ch, out_ch) in enumerate(zip(kernel_size, in_splits, out_splits)):
      conv_groups = in_ch if depthwise else 1
      # use add_module to keep key space clean
      self.add_module(
          str(idx),
          _create_conv2d_pad(in_ch, out_ch, k, stride=stride, padding=padding,
                             dilation=dilation, groups=conv_groups, **kwargs))
    self.splits = in_splits

  def forward(self, x):
    x_split = torch.split(x, self.splits, 1)
    x_out = [c(x_split[i]) for i, c in enumerate(self.values())]
    x = torch.cat(x_out, 1)
    return x


def _get_condconv_initializer(initializer, num_experts, expert_shape):
  def condconv_initializer(weight):
    """CondConv initializer function."""
    num_params = np.prod(expert_shape)
    if (len(weight.shape) != 2 or weight.shape[0] != num_experts or weight.shape[1] != num_params):
      raise (ValueError('CondConv variables must have shape [num_experts, num_params]'))
    for i in range(num_experts):
      initializer(weight[i].view(expert_shape))
  return condconv_initializer


def _to_tuple(x, repeat=2):
  if not isinstance(x, (list, tuple)):
    return (x, ) * repeat
  else:
    assert len(x) == repeat
    return x


class CondConv2d(nn.Module):
  """ Conditionally Parameterized Convolution

    Inspired by: https://github.com/tensorflow/tpu/blob/master/models/official/efficientnet/condconv/condconv_layers.py

    Grouped convolution hackery for parallel execution of the per-sample kernel filters inspired by this discussion:
    https://github.com/pytorch/pytorch/issues/17983

    Paper: CondConv: Conditionally Parameterized Convolutions for Efficient Inference
    (https://arxiv.org/abs/1904.04971)

  """
  __constants__ = ['in_channels', 'out_channels', 'dynamic_padding']

  def __init__(self, in_channels, out_channels, kernel_size=3,
               stride=1, padding='', dilation=1, groups=1, bias=False, num_experts=4):
    super(CondConv2d, self).__init__()

    self.in_channels = in_channels
    self.out_channels = out_channels
    self.kernel_size = _to_tuple(kernel_size)
    self.stride = _to_tuple(stride)
    pad_value, is_dynamic = _get_padding_value(padding, kernel_size, stride=stride, dilation=dilation)
    self.dynamic_padding = is_dynamic  # if in forward to work with torchscript
    self.padding = _to_tuple(pad_value)
    self.dilation = _to_tuple(dilation)
    self.groups = groups
    self.num_experts = num_experts

    self.weight_shape = (self.out_channels, self.in_channels // self.groups) + self.kernel_size
    weight_num_param = 1

    for wd in self.weight_shape:
      weight_num_param *= wd
    self.weight = torch.nn.Parameter(torch.Tensor(self.num_experts, weight_num_param))

    if bias:
      self.bias_shape = (self.out_channels,)
      self.bias = torch.nn.Parameter(torch.Tensor(self.num_experts, self.out_channels))
    else:
      self.register_parameter('bias', None)

    self.reset_parameters()

  def reset_parameters(self):
    init_weight = _get_condconv_initializer(functools.partial(
        nn.init.kaiming_uniform_, a=math.sqrt(5)), self.num_experts, self.weight_shape)
    init_weight(self.weight)

    if self.bias is not None:
      fan_in = np.prod(self.weight_shape[1:])
      bound = 1 / math.sqrt(fan_in)
      init_bias = _get_condconv_initializer(functools.partial(
          nn.init.uniform_, a=-bound, b=bound), self.num_experts, self.bias_shape)
      init_bias(self.bias)

  def forward(self, x, routing_weights):
    B, C, H, W = x.shape
    weight = torch.matmul(routing_weights, self.weight)
    new_weight_shape = (B * self.out_channels, self.in_channels // self.groups) + self.kernel_size
    weight = weight.view(new_weight_shape)
    bias = None

    if self.bias is not None:
      bias = torch.matmul(routing_weights, self.bias)
      bias = bias.view(B * self.out_channels)

    # move batch elements with channels so each batch element can be efficiently convolved with separate kernel
    x = x.view(1, B * C, H, W)
    if self.dynamic_padding:
      out = _conv2d_same(x, weight, bias, stride=self.stride, padding=self.padding,
                         dilation=self.dilation, groups=self.groups * B)
    else:
      out = F.conv2d(x, weight, bias, stride=self.stride, padding=self.padding,
                     dilation=self.dilation, groups=self.groups * B)

    out = out.permute([1, 0, 2, 3]).view(B, self.out_channels, out.shape[-2], out.shape[-1])
    return out


#!<-----------------------------------------------------------------------------
#!< ConvBlocks
#!<-----------------------------------------------------------------------------


def _create_conv2d(in_channels, out_channels, kernel_size, **kwargs):
  """Select a 2d convolution implementation based on arguments

    Creates and returns one of torch.nn.Conv2d, Conv2dSame, MixedConv2d, or CondConv2d.
    Used extensively by EfficientNet, MobileNetv3 and related networks.

  """
  if isinstance(kernel_size, list):
    # MixNet + CondConv combo not supported currently
    assert 'num_experts' not in kwargs
    # MixedConv groups are defined by kernel list
    assert 'groups' not in kwargs
    # We're going to use only lists for defining the MixedConv2d kernel groups,
    # ints, tuples, other iterables will continue to pass to normal conv and specify h, w.
    m = MixedConv2d(in_channels, out_channels, kernel_size, **kwargs)
  else:
    depthwise = kwargs.pop('depthwise', False)
    # for DW out_channels must be multiple of in_channels as must have out_channels % groups == 0
    groups = in_channels if depthwise else kwargs.pop('groups', 1)
    if 'num_experts' in kwargs and kwargs['num_experts'] > 0:
      m = CondConv2d(in_channels, out_channels, kernel_size, groups=groups, **kwargs)
    else:
      # SameConv2d or Conv2d
      m = _create_conv2d_pad(in_channels, out_channels, kernel_size, groups=groups, **kwargs)
  return m


class ConvBnAct(nn.Module):
  """ Conv + Norm Layer + Activation w/ optional skip connection
  """

  def __init__(self, in_chs, out_chs, kernel_size, stride=1, dilation=1, pad_type='',
               skip=False, act_layer=nn.ReLU, norm_layer=nn.BatchNorm2d, drop_path_rate=0.):
    super(ConvBnAct, self).__init__()
    self.has_residual = skip and stride == 1 and in_chs == out_chs
    self.drop_path_rate = drop_path_rate
    self.conv = _create_conv2d(in_chs, out_chs, kernel_size, stride=stride, dilation=dilation, padding=pad_type)
    self.bn1 = norm_layer(out_chs)
    self.act1 = act_layer()

  def feature_info(self, location):
    if location == 'expansion':  # output of conv after act, same as block coutput
      info = dict(module='act1', hook_type='forward', num_chs=self.conv.out_channels)
    else:  # location == 'bottleneck', block output
      info = dict(module='', hook_type='', num_chs=self.conv.out_channels)
    return info

  def forward(self, x):
    shortcut = x
    x = self.conv(x)
    x = self.bn1(x)
    x = self.act1(x)
    if self.has_residual:
      # if self.drop_path_rate > 0.:
      #   x = drop_path(x, self.drop_path_rate, self.training)
      x += shortcut
    return x


class DepthwiseSeparableConv(nn.Module):
  """ DepthwiseSeparable block
  Used for DS convs in MobileNet-V1 and in the place of IR blocks that have no expansion
  (factor of 1.0). This is an alternative to having a IR with an optional first pw conv.
  """

  def __init__(
          self, in_chs, out_chs, dw_kernel_size=3, stride=1, dilation=1, pad_type='',
          noskip=False, pw_kernel_size=1, pw_act=False, act_layer=nn.ReLU, norm_layer=nn.BatchNorm2d,
          se_layer=None, drop_path_rate=0.):
    super(DepthwiseSeparableConv, self).__init__()
    self.has_residual = (stride == 1 and in_chs == out_chs) and not noskip
    self.has_pw_act = pw_act  # activation after point-wise conv
    self.drop_path_rate = drop_path_rate

    self.conv_dw = _create_conv2d(
        in_chs, in_chs, dw_kernel_size, stride=stride, dilation=dilation, padding=pad_type, depthwise=True)
    self.bn1 = norm_layer(in_chs)
    self.act1 = act_layer()

    # Squeeze-and-excitation
    self.se = se_layer(in_chs, act_layer=act_layer) if se_layer else nn.Identity()

    self.conv_pw = _create_conv2d(in_chs, out_chs, pw_kernel_size, padding=pad_type)
    self.bn2 = norm_layer(out_chs)
    self.act2 = act_layer() if self.has_pw_act else nn.Identity()

  def feature_info(self, location):
    if location == 'expansion':  # after SE, input to PW
      info = dict(module='conv_pw', hook_type='forward_pre', num_chs=self.conv_pw.in_channels)
    else:  # location == 'bottleneck', block output
      info = dict(module='', hook_type='', num_chs=self.conv_pw.out_channels)
    return info

  def forward(self, x):
    shortcut = x

    x = self.conv_dw(x)
    x = self.bn1(x)
    x = self.act1(x)

    x = self.se(x)

    x = self.conv_pw(x)
    x = self.bn2(x)
    x = self.act2(x)

    if self.has_residual:
      if self.drop_path_rate > 0.:
        x = drop_path(x, self.drop_path_rate, self.training)
      x += shortcut
    return x


class InvertedResidual(nn.Module):
  """ Inverted residual block w/ optional SE

  Originally used in MobileNet-V2 - https://arxiv.org/abs/1801.04381v4, this layer is often
  referred to as 'MBConv' for (Mobile inverted bottleneck conv) and is also used in
    * MNasNet - https://arxiv.org/abs/1807.11626
    * EfficientNet - https://arxiv.org/abs/1905.11946
    * MobileNet-V3 - https://arxiv.org/abs/1905.02244
  """

  def __init__(self, in_chs, out_chs, dw_kernel_size=3, stride=1, dilation=1, pad_type='',
               noskip=False, exp_ratio=1.0, exp_kernel_size=1, pw_kernel_size=1, act_layer=nn.ReLU,
               norm_layer=nn.BatchNorm2d, se_layer=None, conv_kwargs=None, drop_path_rate=0.):
    super(InvertedResidual, self).__init__()
    conv_kwargs = conv_kwargs or {}
    mid_chs = _make_divisible(in_chs * exp_ratio)
    self.has_residual = (in_chs == out_chs and stride == 1) and not noskip
    self.drop_path_rate = drop_path_rate

    # Point-wise expansion
    self.conv_pw = _create_conv2d(in_chs, mid_chs, exp_kernel_size, padding=pad_type, **conv_kwargs)
    self.bn1 = norm_layer(mid_chs)
    self.act1 = act_layer()

    # Depth-wise convolution
    self.conv_dw = _create_conv2d(mid_chs, mid_chs, dw_kernel_size, stride=stride, dilation=dilation,
                                  padding=pad_type, depthwise=True, **conv_kwargs)
    self.bn2 = norm_layer(mid_chs)
    self.act2 = act_layer()

    # Squeeze-and-excitation
    self.se = se_layer(mid_chs, act_layer=act_layer) if se_layer else nn.Identity()

    # Point-wise linear projection
    self.conv_pwl = _create_conv2d(mid_chs, out_chs, pw_kernel_size, padding=pad_type, **conv_kwargs)
    self.bn3 = norm_layer(out_chs)

  def feature_info(self, location):
    if location == 'expansion':  # after SE, input to PWL
      info = dict(module='conv_pwl', hook_type='forward_pre', num_chs=self.conv_pwl.in_channels)
    else:  # location == 'bottleneck', block output
      info = dict(module='', hook_type='', num_chs=self.conv_pwl.out_channels)
    return info

  def forward(self, x):
    shortcut = x

    # Point-wise expansion
    x = self.conv_pw(x)
    x = self.bn1(x)
    x = self.act1(x)

    # Depth-wise convolution
    x = self.conv_dw(x)
    x = self.bn2(x)
    x = self.act2(x)

    # Squeeze-and-excitation
    x = self.se(x)

    # Point-wise linear projection
    x = self.conv_pwl(x)
    x = self.bn3(x)

    if self.has_residual:
      # if self.drop_path_rate > 0.:
      #   x = drop_path(x, self.drop_path_rate, self.training)
      x += shortcut

    return x


class CondConvResidual(InvertedResidual):
  """ Inverted residual block w/ CondConv routing"""

  def __init__(self, in_chs, out_chs, dw_kernel_size=3, stride=1, dilation=1, pad_type='',
               noskip=False, exp_ratio=1.0, exp_kernel_size=1, pw_kernel_size=1, act_layer=nn.ReLU,
               norm_layer=nn.BatchNorm2d, se_layer=None, num_experts=0, drop_path_rate=0.):

    self.num_experts = num_experts
    conv_kwargs = dict(num_experts=self.num_experts)

    super(CondConvResidual, self).__init__(in_chs, out_chs, dw_kernel_size=dw_kernel_size, stride=stride, dilation=dilation, pad_type=pad_type,
                                           act_layer=act_layer, noskip=noskip, exp_ratio=exp_ratio, exp_kernel_size=exp_kernel_size,
                                           pw_kernel_size=pw_kernel_size, se_layer=se_layer, norm_layer=norm_layer, conv_kwargs=conv_kwargs,
                                           drop_path_rate=drop_path_rate)

    self.routing_fn = nn.Linear(in_chs, self.num_experts)

  def forward(self, x):
    shortcut = x

    # CondConv routing
    pooled_inputs = F.adaptive_avg_pool2d(x, 1).flatten(1)
    routing_weights = torch.sigmoid(self.routing_fn(pooled_inputs))

    # Point-wise expansion
    x = self.conv_pw(x, routing_weights)
    x = self.bn1(x)
    x = self.act1(x)

    # Depth-wise convolution
    x = self.conv_dw(x, routing_weights)
    x = self.bn2(x)
    x = self.act2(x)

    # Squeeze-and-excitation
    x = self.se(x)

    # Point-wise linear projection
    x = self.conv_pwl(x, routing_weights)
    x = self.bn3(x)

    if self.has_residual:
      # if self.drop_path_rate > 0.:
      #   x = drop_path(x, self.drop_path_rate, self.training)
      x += shortcut
    return x


class EdgeResidual(nn.Module):
  """ Residual block with expansion convolution followed by pointwise-linear w/ stride

  Originally introduced in `EfficientNet-EdgeTPU: Creating Accelerator-Optimized Neural Networks with AutoML`
      - https://ai.googleblog.com/2019/08/efficientnet-edgetpu-creating.html

  This layer is also called FusedMBConv in the MobileDet, EfficientNet-X, and EfficientNet-V2 papers
    * MobileDet - https://arxiv.org/abs/2004.14525
    * EfficientNet-X - https://arxiv.org/abs/2102.05610
    * EfficientNet-V2 - https://arxiv.org/abs/2104.00298
  """

  def __init__(self, in_chs, out_chs, exp_kernel_size=3, stride=1, dilation=1, pad_type='',
               force_in_chs=0, noskip=False, exp_ratio=1.0, pw_kernel_size=1, act_layer=nn.ReLU,
               norm_layer=nn.BatchNorm2d, se_layer=None, drop_path_rate=0.):
    super(EdgeResidual, self).__init__()
    if force_in_chs > 0:
      mid_chs = _make_divisible(force_in_chs * exp_ratio)
    else:
      mid_chs = _make_divisible(in_chs * exp_ratio)
    has_se = se_layer is not None and se_ratio > 0.
    self.has_residual = (in_chs == out_chs and stride == 1) and not noskip
    self.drop_path_rate = drop_path_rate

    # Expansion convolution
    self.conv_exp = _create_conv2d(
        in_chs, mid_chs, exp_kernel_size, stride=stride, dilation=dilation, padding=pad_type)
    self.bn1 = norm_layer(mid_chs)
    self.act1 = act_layer()

    # Squeeze-and-excitation
    self.se = se_layer(mid_chs, act_layer=act_layer) if se_layer else nn.Identity()

    # Point-wise linear projection
    self.conv_pwl = _create_conv2d(mid_chs, out_chs, pw_kernel_size, padding=pad_type)
    self.bn2 = norm_layer(out_chs)

  def feature_info(self, location):
    if location == 'expansion':  # after SE, before PWL
      info = dict(module='conv_pwl', hook_type='forward_pre', num_chs=self.conv_pwl.in_channels)
    else:  # location == 'bottleneck', block output
      info = dict(module='', hook_type='', num_chs=self.conv_pwl.out_channels)
    return info

  def forward(self, x):
    shortcut = x

    # Expansion convolution
    x = self.conv_exp(x)
    x = self.bn1(x)
    x = self.act1(x)

    # Squeeze-and-excitation
    x = self.se(x)

    # Point-wise linear projection
    x = self.conv_pwl(x)
    x = self.bn2(x)

    if self.has_residual:
      # if self.drop_path_rate > 0.:
      #   x = drop_path(x, self.drop_path_rate, self.training)
      x += shortcut

    return x

#!<-----------------------------------------------------------------------------
#!< Deformable Convolution
#!<-----------------------------------------------------------------------------


class DeformConvFunction(Function):

  @staticmethod
  def forward(ctx, input, offset, weight, stride=1, padding=0,
              dilation=1, groups=1, deformable_groups=1, im2col_step=64):
    if input is not None and input.dim() != 4:
      raise ValueError("Expected 4D tensor as input, got {}D tensor instead.".format(input.dim()))

    ctx.stride = _pair(stride)
    ctx.padding = _pair(padding)
    ctx.dilation = _pair(dilation)
    ctx.groups = groups
    ctx.deformable_groups = deformable_groups
    ctx.im2col_step = im2col_step

    ctx.save_for_backward(input, offset, weight)

    output = input.new_empty(DeformConvFunction._output_size(input, weight, ctx.padding, ctx.dilation, ctx.stride))

    ctx.bufs_ = [input.new_empty(0), input.new_empty(0)]  # columns, ones

    if not input.is_cuda:
      raise NotImplementedError
    else:
      cur_im2col_step = min(ctx.im2col_step, input.shape[0])
      assert (input.shape[0] % cur_im2col_step) == 0, 'im2col step must divide batchsize'
      _C.deform_conv_forward(input,
                             weight,
                             offset,
                             output,
                             ctx.bufs_[0],
                             ctx.bufs_[1],
                             weight.size(3),
                             weight.size(2),
                             ctx.stride[1],
                             ctx.stride[0],
                             ctx.padding[1],
                             ctx.padding[0],
                             ctx.dilation[1],
                             ctx.dilation[0],
                             ctx.groups,
                             ctx.deformable_groups,
                             cur_im2col_step)
    return output

  @staticmethod
  @once_differentiable
  def backward(ctx, grad_output):
    input, offset, weight = ctx.saved_tensors

    grad_input = grad_offset = grad_weight = None

    if not grad_output.is_cuda:
      raise NotImplementedError
    else:
      cur_im2col_step = min(ctx.im2col_step, input.shape[0])
      assert (input.shape[0] % cur_im2col_step) == 0, 'im2col step must divide batchsize'

      if ctx.needs_input_grad[0] or ctx.needs_input_grad[1]:
        grad_input = torch.zeros_like(input)
        grad_offset = torch.zeros_like(offset)
        _C.deform_conv_backward_input(input,
                                      offset,
                                      grad_output,
                                      grad_input,
                                      grad_offset,
                                      weight,
                                      ctx.bufs_[0],
                                      weight.size(3),
                                      weight.size(2),
                                      ctx.stride[1],
                                      ctx.stride[0],
                                      ctx.padding[1],
                                      ctx.padding[0],
                                      ctx.dilation[1],
                                      ctx.dilation[0],
                                      ctx.groups,
                                      ctx.deformable_groups,
                                      cur_im2col_step)

      if ctx.needs_input_grad[2]:
        grad_weight = torch.zeros_like(weight)
        _C.deform_conv_backward_parameters(input,
                                           offset,
                                           grad_output,
                                           grad_weight,
                                           ctx.bufs_[0],
                                           ctx.bufs_[1],
                                           weight.size(3),
                                           weight.size(2),
                                           ctx.stride[1],
                                           ctx.stride[0],
                                           ctx.padding[1],
                                           ctx.padding[0],
                                           ctx.dilation[1],
                                           ctx.dilation[0],
                                           ctx.groups,
                                           ctx.deformable_groups,
                                           1,
                                           cur_im2col_step)

    return (grad_input, grad_offset, grad_weight, None, None, None, None, None)

  @staticmethod
  def _output_size(input, weight, padding, dilation, stride):
    channels = weight.size(0)
    output_size = (input.size(0), channels)

    for d in range(input.dim() - 2):
      in_size = input.size(d + 2)
      pad = padding[d]
      kernel = dilation[d] * (weight.size(d + 2) - 1) + 1
      stride_ = stride[d]
      output_size += ((in_size + (2 * pad) - kernel) // stride_ + 1, )

    if not all(map(lambda s: s > 0, output_size)):
      raise ValueError("convolution input is too small (output would be {})".format('x'.join(map(str, output_size))))

    return output_size


class ModulatedDeformConvFunction(Function):

  @staticmethod
  def forward(ctx, input, offset, mask, weight, bias=None, stride=1,
              padding=0, dilation=1, groups=1, deformable_groups=1):
    ctx.stride = stride
    ctx.padding = padding
    ctx.dilation = dilation
    ctx.groups = groups
    ctx.deformable_groups = deformable_groups
    ctx.with_bias = bias is not None

    if not ctx.with_bias:
      bias = input.new_empty(1)  # fake tensor

    if not input.is_cuda:
      raise NotImplementedError

    if weight.requires_grad or mask.requires_grad or offset.requires_grad or input.requires_grad:
      ctx.save_for_backward(input, offset, mask, weight, bias)

    output = input.new_empty(ModulatedDeformConvFunction._infer_shape(ctx, input, weight))

    ctx._bufs = [input.new_empty(0), input.new_empty(0)]

    _C.modulated_deform_conv_forward(input,
                                     weight,
                                     bias,
                                     ctx._bufs[0],
                                     offset,
                                     mask,
                                     output,
                                     ctx._bufs[1],
                                     weight.shape[2],
                                     weight.shape[3],
                                     ctx.stride,
                                     ctx.stride,
                                     ctx.padding,
                                     ctx.padding,
                                     ctx.dilation,
                                     ctx.dilation,
                                     ctx.groups,
                                     ctx.deformable_groups,
                                     ctx.with_bias)
    return output

  @staticmethod
  @once_differentiable
  def backward(ctx, grad_output):
    if not grad_output.is_cuda:
      raise NotImplementedError

    input, offset, mask, weight, bias = ctx.saved_tensors
    grad_input = torch.zeros_like(input)
    grad_offset = torch.zeros_like(offset)
    grad_mask = torch.zeros_like(mask)
    grad_weight = torch.zeros_like(weight)
    grad_bias = torch.zeros_like(bias)
    _C.modulated_deform_conv_backward(input,
                                      weight,
                                      bias,
                                      ctx._bufs[0],
                                      offset,
                                      mask,
                                      ctx._bufs[1],
                                      grad_input,
                                      grad_weight,
                                      grad_bias,
                                      grad_offset,
                                      grad_mask,
                                      grad_output,
                                      weight.shape[2],
                                      weight.shape[3],
                                      ctx.stride,
                                      ctx.stride,
                                      ctx.padding,
                                      ctx.padding,
                                      ctx.dilation,
                                      ctx.dilation,
                                      ctx.groups,
                                      ctx.deformable_groups,
                                      ctx.with_bias)

    if not ctx.with_bias:
      grad_bias = None

    return (grad_input, grad_offset, grad_mask, grad_weight, grad_bias,
            None, None, None, None, None)

  @staticmethod
  def _infer_shape(ctx, input, weight):
    n = input.size(0)
    channels_out = weight.size(0)
    height, width = input.shape[2:4]
    kernel_h, kernel_w = weight.shape[2:4]
    height_out = (height + 2 * ctx.padding - (ctx.dilation * (kernel_h - 1) + 1)) // ctx.stride + 1
    width_out = (width + 2 * ctx.padding - (ctx.dilation * (kernel_w - 1) + 1)) // ctx.stride + 1
    return n, channels_out, height_out, width_out


deform_conv = DeformConvFunction.apply
modulated_deform_conv = ModulatedDeformConvFunction.apply


class DeformConv(nn.Module):

  def __init__(self, in_channels, out_channels, kernel_size, stride=1,
               padding=0, dilation=1, groups=1, deformable_groups=1, bias=False):
    assert not bias
    super(DeformConv, self).__init__()
    self.with_bias = bias

    assert in_channels % groups == 0, 'in_channels {} cannot be divisible by groups {}'.format(in_channels, groups)
    assert out_channels % groups == 0, 'out_channels {} cannot be divisible by groups {}'.format(out_channels, groups)

    self.in_channels = in_channels
    self.out_channels = out_channels
    self.kernel_size = _pair(kernel_size)
    self.stride = _pair(stride)
    self.padding = _pair(padding)
    self.dilation = _pair(dilation)
    self.groups = groups
    self.deformable_groups = deformable_groups

    self.weight = nn.Parameter(torch.Tensor(out_channels, in_channels // self.groups, *self.kernel_size))

    self.reset_parameters()

  def reset_parameters(self):
    n = self.in_channels
    for k in self.kernel_size:
      n *= k
    stdv = 1. / math.sqrt(n)
    self.weight.data.uniform_(-stdv, stdv)

  def forward(self, input, offset):
    return deform_conv(input, offset, self.weight, self.stride, self.padding,
                       self.dilation, self.groups, self.deformable_groups)

  def __repr__(self):
    return "".join([
        "{}(".format(self.__class__.__name__),
        "in_channels={}, ".format(self.in_channels),
        "out_channels={}, ".format(self.out_channels),
        "kernel_size={}, ".format(self.kernel_size),
        "stride={}, ".format(self.stride),
        "dilation={}, ".format(self.dilation),
        "padding={}, ".format(self.padding),
        "groups={}, ".format(self.groups),
        "deformable_groups={}, ".format(self.deformable_groups),
        "bias={})".format(self.with_bias)])


class ModulatedDeformConv(nn.Module):
  def __init__(self, in_channels, out_channels, kernel_size, stride=1,
               padding=0, dilation=1, groups=1, deformable_groups=1, bias=True):
    super(ModulatedDeformConv, self).__init__()
    self.in_channels = in_channels
    self.out_channels = out_channels
    self.kernel_size = _pair(kernel_size)
    self.stride = stride
    self.padding = padding
    self.dilation = dilation
    self.groups = groups
    self.deformable_groups = deformable_groups
    self.with_bias = bias

    self.weight = nn.Parameter(torch.Tensor(
        out_channels,
        in_channels // groups,
        *self.kernel_size))

    if bias:
      self.bias = nn.Parameter(torch.Tensor(out_channels))
    else:
      self.register_parameter('bias', None)

    self.reset_parameters()

  def reset_parameters(self):
    n = self.in_channels
    for k in self.kernel_size:
      n *= k
    stdv = 1. / math.sqrt(n)
    self.weight.data.uniform_(-stdv, stdv)
    if self.bias is not None:
      self.bias.data.zero_()

  def forward(self, input, offset, mask):
    return modulated_deform_conv(
        input, offset, mask, self.weight, self.bias, self.stride,
        self.padding, self.dilation, self.groups, self.deformable_groups)

  def __repr__(self):
    return "".join([
        "{}(".format(self.__class__.__name__),
        "in_channels={}, ".format(self.in_channels),
        "out_channels={}, ".format(self.out_channels),
        "kernel_size={}, ".format(self.kernel_size),
        "stride={}, ".format(self.stride),
        "dilation={}, ".format(self.dilation),
        "padding={}, ".format(self.padding),
        "groups={}, ".format(self.groups),
        "deformable_groups={}, ".format(self.deformable_groups),
        "bias={})".format(self.with_bias),
    ])


class ModulatedDeformConvPack(ModulatedDeformConv):

  def __init__(self, in_channels, out_channels, kernel_size, stride=1,
               padding=0, dilation=1, groups=1, deformable_groups=1, bias=True):
    super(ModulatedDeformConvPack, self).__init__(in_channels,
                                                  out_channels,
                                                  kernel_size,
                                                  stride,
                                                  padding,
                                                  dilation,
                                                  groups,
                                                  deformable_groups,
                                                  bias)

    self.conv_offset_mask = nn.Conv2d(self.in_channels // self.groups,
                                      self.deformable_groups * 3 *
                                      self.kernel_size[0] * self.kernel_size[1],
                                      kernel_size=self.kernel_size,
                                      stride=_pair(self.stride),
                                      padding=_pair(self.padding),
                                      bias=True)
    self.init_offset()

  def init_offset(self):
    self.conv_offset_mask.weight.data.zero_()
    self.conv_offset_mask.bias.data.zero_()

  def forward(self, input):
    out = self.conv_offset_mask(input)
    o1, o2, mask = torch.chunk(out, 3, dim=1)
    offset = torch.cat((o1, o2), dim=1)
    mask = torch.sigmoid(mask)
    return modulated_deform_conv(input,
                                 offset,
                                 mask,
                                 self.weight,
                                 self.bias,
                                 self.stride,
                                 self.padding,
                                 self.dilation,
                                 self.groups,
                                 self.deformable_groups)


class ConvModule(nn.Module):

  def __init__(self, conv: nn.Module, act=None, norm=None):
    super(ConvModule, self).__init__()
    self.conv = conv
    self.with_act, self.with_norm = False, False
    if act is not None:
      self.activate = act
      self.with_act = True
    if norm is not None:
      self.norm = norm
      self.with_norm = True

  def forward(self, x):
    x = self.conv(x)
    if self.with_act:
      x = self.activate(x)
    if self.with_norm:
      x = self.norm(x)
    return x

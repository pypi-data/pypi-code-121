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
import torch
from torch import nn
from torch.nn.modules.utils import _ntuple

#!<-----------------------------------------------------------------------------
#!< For some tasks, the output shape is related with input data (e.g. detection),
#!< which will result in that someone dimension is equal to 0, like [0, 3, 17, 17].
#!< So, while we need to execuate the operation (in graph) but do nothing.
#!<-----------------------------------------------------------------------------


class _NewEmptyTensorOp(torch.autograd.Function):
  @staticmethod
  def forward(ctx, x, new_shape):
    # although the new_empty will result a segment of raw memory, the new_shape
    # include a dimension 0. in face, x will do not include any data.
    ctx.shape = x.shape
    return x.new_empty(new_shape)

  @staticmethod
  def backward(ctx, grad):
    shape = ctx.shape
    return _NewEmptyTensorOp.apply(grad, shape), None


class EmptyConv2d(torch.nn.Conv2d):
  def forward(self, x):
    if x.numel() > 0:
      return super(EmptyConv2d, self).forward(x)
    output_shape = [
        (i + 2 * p - (di * (k - 1) + 1)) // d + 1
        for i, p, di, k, d in zip(
            x.shape[-2:],
            self.padding,
            self.dilation,
            self.kernel_size,
            self.stride)]
    output_shape = [x.shape[0], self.weight.shape[0]] + output_shape
    return _NewEmptyTensorOp.apply(x, output_shape)


class EmptyConvTranspose2d(torch.nn.ConvTranspose2d):
  def forward(self, x):
    if x.numel() > 0:
      return super(EmptyConvTranspose2d, self).forward(x)
    output_shape = [
        (i - 1) * d - 2 * p + (di * (k - 1) + 1) + op
        for i, p, di, k, d, op in zip(
            x.shape[-2:],
            self.padding,
            self.dilation,
            self.kernel_size,
            self.stride,
            self.output_padding)]
    output_shape = [x.shape[0], self.bias.shape[0]] + output_shape
    return _NewEmptyTensorOp.apply(x, output_shape)


class EmptyBatchNorm2d(torch.nn.BatchNorm2d):
  def forward(self, x):
    if x.numel() > 0:
      return super(EmptyBatchNorm2d, self).forward(x)
    # get output shape
    output_shape = x.shape
    return _NewEmptyTensorOp.apply(x, output_shape)


def EmptyInterpolate(inputs,
                     size=None,
                     scale_factor=None,
                     mode="nearest",
                     align_corners=None):
  if inputs.numel() > 0:
    return torch.nn.functional.interpolate(
        inputs, size, scale_factor, mode, align_corners)

  def _check_size_scale_factor(dim):
    if size is None and scale_factor is None:
      raise ValueError("either size or scale_factor should be defined")
    if size is not None and scale_factor is not None:
      raise ValueError("only one of size or scale_factor should be defined")
    if (scale_factor is not None
        and isinstance(scale_factor, tuple)
            and len(scale_factor) != dim):
      raise ValueError(
          "scale_factor shape must match inputs shape. "
          "Inputs is {}D, scale_factor size is {}".format(
              dim, len(scale_factor)))

  def _output_size(dim):
    _check_size_scale_factor(dim)
    if size is not None:
      return size
    scale_factors = _ntuple(dim)(scale_factor)
    # math.floor might return float in py2.7
    return [int(math.floor(inputs.size(i + 2) * scale_factors[i]))
            for i in range(dim)]

  output_shape = tuple(_output_size(2))
  output_shape = inputs.shape[:-2] + output_shape
  return _NewEmptyTensorOp.apply(inputs, output_shape)


class EmptyLayer(nn.Module):
  def __init__(self):
    """Placeholder for 'route' and 'shortcut' layers"""
    super(EmptyLayer, self).__init__()

#!<-----------------------------------------------------------------------------
#!< For some training task, we usd pretrain model as well as keeping the vanilla
#!< batch norm statistic.
#!<-----------------------------------------------------------------------------


class FrozenBatchNorm2d(nn.Module):
  def __init__(self, n):
    r"""BatchNorm2d where the batch statistics and the affine parameters are fixed
    """
    super(FrozenBatchNorm2d, self).__init__()
    self.register_buffer("weight", torch.ones(n))
    self.register_buffer("bias", torch.zeros(n))
    self.register_buffer("running_mean", torch.zeros(n))
    self.register_buffer("running_var", torch.ones(n))

  def forward(self, x):
    scale = self.weight * self.running_var.rsqrt()
    bias = self.bias - self.running_mean * scale
    scale = scale.reshape(1, -1, 1, 1)
    bias = bias.reshape(1, -1, 1, 1)
    return x * scale + bias

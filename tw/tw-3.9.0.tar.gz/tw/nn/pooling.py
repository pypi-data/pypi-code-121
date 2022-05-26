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
r"""Pooling
"""

import torch
from torch import nn
from torch.nn import functional as F
from torch.autograd import Function
from torch.autograd.function import once_differentiable
from torch.nn.modules.pooling import AdaptiveMaxPool2d
from torch.nn.modules.utils import _pair

try:
  from tw import _C
except ImportError:
  _C = None

__all__ = [
    'DeformRoIPoolingFunction',
    'DeformRoIPooling',
    'DeformRoIPoolingPack',
    'ModulatedDeformRoIPoolingPack',
    'RoIAlign',
    'RoIPool',
    'ChannelMaxPool',
    'ChannelAvgPool',
    'CrissCrossAttention',
    'AtrousSpatialPyramidPooling',
    'AdaptiveAvgMaxPool2d',
    'AdaptiveCatAvgMaxPool2d',
]

#!<-----------------------------------------------------------------------------
#!< Pooling
#!<-----------------------------------------------------------------------------


class AdaptiveAvgMaxPool2d(nn.Module):

  def ___init__(self, output_size=1):
    super(AdaptiveAvgMaxPool2d, self).__init__()
    self.output_size = output_size

  def forward(self, x):
    x_avg = F.adaptive_avg_pool2d(x, self.output_size)
    x_max = F.adaptive_max_pool2d(x, self.output_size)
    return 0.5 * (x_avg + x_max)


class AdaptiveCatAvgMaxPool2d(nn.Module):

  def ___init__(self, output_size=1):
    super(AdaptiveCatAvgMaxPool2d, self).__init__()
    self.output_size = output_size

  def forward(self, x):
    x_avg = F.adaptive_avg_pool2d(x, self.output_size)
    x_max = F.adaptive_max_pool2d(x, self.output_size)
    return torch.cat((x_avg, x_max), 1)

#!<-----------------------------------------------------------------------------
#!< Deformable Pooling
#!<-----------------------------------------------------------------------------


class DeformRoIPoolingFunction(Function):
  @staticmethod
  def forward(
          ctx,
          data,
          rois,
          offset,
          spatial_scale,
          out_size,
          out_channels,
          no_trans,
          group_size=1,
          part_size=None,
          sample_per_part=4,
          trans_std=.0):
    ctx.spatial_scale = spatial_scale
    ctx.out_size = out_size
    ctx.out_channels = out_channels
    ctx.no_trans = no_trans
    ctx.group_size = group_size
    ctx.part_size = out_size if part_size is None else part_size
    ctx.sample_per_part = sample_per_part
    ctx.trans_std = trans_std

    assert 0.0 <= ctx.trans_std <= 1.0
    if not data.is_cuda:
      raise NotImplementedError

    n = rois.shape[0]
    output = data.new_empty(n, out_channels, out_size, out_size)
    output_count = data.new_empty(n, out_channels, out_size, out_size)
    _C.deform_psroi_pooling_forward(
        data,
        rois,
        offset,
        output,
        output_count,
        ctx.no_trans,
        ctx.spatial_scale,
        ctx.out_channels,
        ctx.group_size,
        ctx.out_size,
        ctx.part_size,
        ctx.sample_per_part,
        ctx.trans_std)

    if data.requires_grad or rois.requires_grad or offset.requires_grad:
      ctx.save_for_backward(data, rois, offset)
    ctx.output_count = output_count

    return output

  @staticmethod
  @once_differentiable
  def backward(ctx, grad_output):
    if not grad_output.is_cuda:
      raise NotImplementedError

    data, rois, offset = ctx.saved_tensors
    output_count = ctx.output_count
    grad_input = torch.zeros_like(data)
    grad_rois = None
    grad_offset = torch.zeros_like(offset)

    _C.deform_psroi_pooling_backward(
        grad_output,
        data,
        rois,
        offset,
        output_count,
        grad_input,
        grad_offset,
        ctx.no_trans,
        ctx.spatial_scale,
        ctx.out_channels,
        ctx.group_size,
        ctx.out_size,
        ctx.part_size,
        ctx.sample_per_part,
        ctx.trans_std)
    return (grad_input, grad_rois, grad_offset, None, None, None, None, None, None, None, None)


deform_roi_pooling = DeformRoIPoolingFunction.apply


class DeformRoIPooling(nn.Module):

  def __init__(self,
               spatial_scale,
               out_size,
               out_channels,
               no_trans,
               group_size=1,
               part_size=None,
               sample_per_part=4,
               trans_std=.0):
    super(DeformRoIPooling, self).__init__()
    self.spatial_scale = spatial_scale
    self.out_size = out_size
    self.out_channels = out_channels
    self.no_trans = no_trans
    self.group_size = group_size
    self.part_size = out_size if part_size is None else part_size
    self.sample_per_part = sample_per_part
    self.trans_std = trans_std

  def forward(self, data, rois, offset):
    if self.no_trans:
      offset = data.new_empty(0)
    return deform_roi_pooling(
        data, rois, offset, self.spatial_scale, self.out_size,
        self.out_channels, self.no_trans, self.group_size, self.part_size,
        self.sample_per_part, self.trans_std)


class DeformRoIPoolingPack(DeformRoIPooling):

  def __init__(self,
               spatial_scale,
               out_size,
               out_channels,
               no_trans,
               group_size=1,
               part_size=None,
               sample_per_part=4,
               trans_std=.0,
               deform_fc_channels=1024):
    super(DeformRoIPoolingPack,
          self).__init__(spatial_scale, out_size, out_channels, no_trans,
                         group_size, part_size, sample_per_part, trans_std)

    self.deform_fc_channels = deform_fc_channels

    if not no_trans:
      self.offset_fc = nn.Sequential(
          nn.Linear(self.out_size * self.out_size * self.out_channels,
                    self.deform_fc_channels),
          nn.ReLU(inplace=True),
          nn.Linear(self.deform_fc_channels, self.deform_fc_channels),
          nn.ReLU(inplace=True),
          nn.Linear(self.deform_fc_channels,
                    self.out_size * self.out_size * 2))
      self.offset_fc[-1].weight.data.zero_()
      self.offset_fc[-1].bias.data.zero_()

  def forward(self, data, rois):
    assert data.size(1) == self.out_channels
    if self.no_trans:
      offset = data.new_empty(0)
      return deform_roi_pooling(
          data, rois, offset, self.spatial_scale, self.out_size,
          self.out_channels, self.no_trans, self.group_size,
          self.part_size, self.sample_per_part, self.trans_std)
    else:
      n = rois.shape[0]
      offset = data.new_empty(0)
      x = deform_roi_pooling(data, rois, offset, self.spatial_scale,
                             self.out_size, self.out_channels, True,
                             self.group_size, self.part_size,
                             self.sample_per_part, self.trans_std)
      offset = self.offset_fc(x.view(n, -1))
      offset = offset.view(n, 2, self.out_size, self.out_size)
      return deform_roi_pooling(
          data, rois, offset, self.spatial_scale, self.out_size,
          self.out_channels, self.no_trans, self.group_size,
          self.part_size, self.sample_per_part, self.trans_std)


class ModulatedDeformRoIPoolingPack(DeformRoIPooling):

  def __init__(self,
               spatial_scale,
               out_size,
               out_channels,
               no_trans,
               group_size=1,
               part_size=None,
               sample_per_part=4,
               trans_std=.0,
               deform_fc_channels=1024):
    super(ModulatedDeformRoIPoolingPack, self).__init__(
        spatial_scale, out_size, out_channels, no_trans, group_size,
        part_size, sample_per_part, trans_std)

    self.deform_fc_channels = deform_fc_channels

    if not no_trans:
      self.offset_fc = nn.Sequential(
          nn.Linear(self.out_size * self.out_size * self.out_channels,
                    self.deform_fc_channels),
          nn.ReLU(inplace=True),
          nn.Linear(self.deform_fc_channels, self.deform_fc_channels),
          nn.ReLU(inplace=True),
          nn.Linear(self.deform_fc_channels,
                    self.out_size * self.out_size * 2))
      self.offset_fc[-1].weight.data.zero_()
      self.offset_fc[-1].bias.data.zero_()
      self.mask_fc = nn.Sequential(
          nn.Linear(self.out_size * self.out_size * self.out_channels,
                    self.deform_fc_channels),
          nn.ReLU(inplace=True),
          nn.Linear(self.deform_fc_channels,
                    self.out_size * self.out_size * 1),
          nn.Sigmoid())
      self.mask_fc[2].weight.data.zero_()
      self.mask_fc[2].bias.data.zero_()

  def forward(self, data, rois):
    assert data.size(1) == self.out_channels
    if self.no_trans:
      offset = data.new_empty(0)
      return deform_roi_pooling(
          data, rois, offset, self.spatial_scale, self.out_size,
          self.out_channels, self.no_trans, self.group_size,
          self.part_size, self.sample_per_part, self.trans_std)
    else:
      n = rois.shape[0]
      offset = data.new_empty(0)
      x = deform_roi_pooling(data, rois, offset, self.spatial_scale,
                             self.out_size, self.out_channels, True,
                             self.group_size, self.part_size,
                             self.sample_per_part, self.trans_std)
      offset = self.offset_fc(x.view(n, -1))
      offset = offset.view(n, 2, self.out_size, self.out_size)
      mask = self.mask_fc(x.view(n, -1))
      mask = mask.view(n, 1, self.out_size, self.out_size)
      return deform_roi_pooling(
          data, rois, offset, self.spatial_scale, self.out_size,
          self.out_channels, self.no_trans, self.group_size,
          self.part_size, self.sample_per_part, self.trans_std) * mask


#!<-----------------------------------------------------------------------------
#!< RoI Pooling/Align
#!<-----------------------------------------------------------------------------


class _RoIAlign(Function):
  @staticmethod
  def forward(ctx, fwd_input, roi, output_size, spatial_scale, sampling_ratio):
    ctx.save_for_backward(roi)
    ctx.output_size = _pair(output_size)
    ctx.spatial_scale = spatial_scale
    ctx.sampling_ratio = sampling_ratio
    ctx.input_shape = fwd_input.size()
    outputs = _C.roi_align_forward(fwd_input, roi, spatial_scale, output_size[0], output_size[1], sampling_ratio)
    return outputs

  @staticmethod
  @once_differentiable
  def backward(ctx, grad_output):
    rois, = ctx.saved_tensors
    output_size = ctx.output_size
    spatial_scale = ctx.spatial_scale
    sampling_ratio = ctx.sampling_ratio
    bs, ch, h, w = ctx.input_shape
    grad_input = _C.roi_align_backward(grad_output, rois, spatial_scale,
                                       output_size[0], output_size[1], bs, ch, h, w, sampling_ratio)
    return grad_input, None, None, None, None


class RoIAlign(nn.Module):
  def __init__(self, output_size, spatial_scale, sampling_ratio):
    super(RoIAlign, self).__init__()
    self.output_size = output_size
    self.spatial_scale = spatial_scale
    self.sampling_ratio = sampling_ratio

  def forward(self, inputs, rois):
    return _RoIAlign.apply(inputs, rois, self.output_size, self.spatial_scale, self.sampling_ratio)

  def __repr__(self):
    tmpstr = self.__class__.__name__ + "("
    tmpstr += "output_size=" + str(self.output_size)
    tmpstr += ", spatial_scale=" + str(self.spatial_scale)
    tmpstr += ", sampling_ratio=" + str(self.sampling_ratio)
    tmpstr += ")"
    return tmpstr


class _ROIPool(Function):
  @staticmethod
  def forward(ctx, inputs, roi, output_size, spatial_scale):
    ctx.output_size = _pair(output_size)
    ctx.spatial_scale = spatial_scale
    ctx.input_shape = inputs.size()
    output, argmax = _C.roi_pool_forward(inputs, roi, spatial_scale, output_size[0], output_size[1])
    ctx.save_for_backward(inputs, roi, argmax)
    return output

  @staticmethod
  @once_differentiable
  def backward(ctx, grad_output):
    inputs, rois, argmax = ctx.saved_tensors
    output_size = ctx.output_size
    spatial_scale = ctx.spatial_scale
    bs, ch, h, w = ctx.input_shape
    grad_input = _C.roi_pool_backward(grad_output, inputs, rois, argmax, spatial_scale,
                                      output_size[0], output_size[1], bs, ch, h, w)
    return grad_input, None, None, None


class RoIPool(nn.Module):
  def __init__(self, output_size, spatial_scale):
    """Performs Region of Interest (RoI) Pool operator described in Fast R-CNN

    Args:
        output_size ([int]): the size of the output after the cropping is performed, as (height, width)
        spatial_scale ([float]): a scaling factor that maps the input coordinates to the box coordinates.
        rois: (Tensor[K, 5] or List[Tensor[L, 4]]): the box coordinates in (x1, y1, x2, y2)
            format where the regions will be taken from.
            The coordinate must satisfy ``0 <= x1 < x2`` and ``0 <= y1 < y2``.
            If a single Tensor is passed, then the first column should
            contain the index of the corresponding element in the batch, i.e. a number in ``[0, N - 1]``.
            If a list of Tensors is passed, then each Tensor will correspond to the boxes for an element i
            in the batch.

    Returns:
        Tensor[K, C, output_size[0], output_size[1]]

    """
    super(RoIPool, self).__init__()
    self.output_size = output_size
    self.spatial_scale = spatial_scale

  def forward(self, inputs, rois):
    """roi max pooling.

    Args:
        inputs ([torch.Tensor]): [N, C, H, W]
        rois ([torch.Tensor]): [K, 5] (batch_ind, x1, y1, x2, y2)

    Returns:
        [type]: [description]
    """
    return _ROIPool.apply(inputs, rois, self.output_size, self.spatial_scale)

  def __repr__(self):
    tmpstr = self.__class__.__name__ + "("
    tmpstr += "output_size=" + str(self.output_size)
    tmpstr += ", spatial_scale=" + str(self.spatial_scale)
    tmpstr += ")"
    return tmpstr


#!<-----------------------------------------------------------------------------
#!< Channel Pooling
#!<-----------------------------------------------------------------------------


class ChannelMaxPool(nn.modules.pooling._MaxPoolNd):

  r"""Applies a channel max pooling over an input signal composed of several input
  planes.

    In the simplest case, the output value of the layer with input size
  :math:`(N, C, H, W)` and output :math:`(N, C_{out}, H, W)` can be precisely
  described as:

  """

  def __init__(self, kernel_size, stride=1, dilation=1, return_indices=False, ceil_mode=False):
    assert isinstance(kernel_size, int)
    assert isinstance(stride, int)
    assert isinstance(dilation, int)
    super(ChannelMaxPool, self).__init__(kernel_size=(1, kernel_size),
                                         stride=(1, stride),
                                         padding=0,
                                         dilation=dilation,
                                         return_indices=return_indices,
                                         ceil_mode=ceil_mode)

  def forward(self, inputs):
    assert inputs.dim() == 4, "Input Dim should be 4-dimension"
    # N, C, H, W -> N, W, H, C
    inputs = inputs.transpose(3, 1)
    inputs = F.max_pool2d(inputs, self.kernel_size, self.stride,
                          self.padding, self.dilation, self.ceil_mode,
                          self.return_indices)
    return inputs.transpose(3, 1).contiguous()


class ChannelAvgPool(nn.modules.pooling._AvgPoolNd):

  r"""Applies a channel max pooling over an input signal composed of several input
  planes.

    In the simplest case, the output value of the layer with input size
  :math:`(N, C, H, W)` and output :math:`(N, C_{out}, H, W)` can be precisely
  described as:

  """

  def __init__(self, kernel_size, stride=1, dilation=1, return_indices=False, ceil_mode=False):
    assert isinstance(kernel_size, int)
    assert isinstance(stride, int)
    assert isinstance(dilation, int)
    super(ChannelAvgPool, self).__init__(kernel_size=(1, kernel_size),
                                         stride=(1, stride),
                                         padding=0,
                                         dilation=dilation,
                                         return_indices=return_indices,
                                         ceil_mode=ceil_mode)

  def forward(self, inputs):
    assert inputs.dim() == 4, "Input Dim should be 4-dimension"
    inputs = inputs.transpose(3, 1)
    inputs = F.avg_pool2d(inputs, self.kernel_size, self.stride,
                          self.padding, self.dilation, self.ceil_mode,
                          self.return_indices)
    return inputs.transpose(3, 1).contiguous()


#!<-----------------------------------------------------------------------------
#!< Criss-Cross Pooling
#!<-----------------------------------------------------------------------------


class _CAWeight(torch.autograd.Function):
  @staticmethod
  def forward(ctx, t, f):
    weight = _C.ca_forward(t, f)
    ctx.save_for_backward(t, f)
    return weight

  @staticmethod
  @once_differentiable
  def backward(ctx, dw):
    t, f = ctx.saved_tensors
    dt, df = _C.ca_backward(dw, t, f)
    return dt, df


class _CAMap(torch.autograd.Function):
  @staticmethod
  def forward(ctx, weight, g):
    out = _C.ca_map_forward(weight, g)
    ctx.save_for_backward(weight, g)
    return out

  @staticmethod
  @once_differentiable
  def backward(ctx, dout):
    weight, g = ctx.saved_tensors
    dw, dg = _C.ca_map_backward(dout, weight, g)
    return dw, dg


class CrissCrossAttention(nn.Module):
  """Criss-Cross Attention Module"""

  def __init__(self, in_channels):
    super(CrissCrossAttention, self).__init__()
    self.query_conv = nn.Conv2d(in_channels, in_channels // 8, 1)
    self.key_conv = nn.Conv2d(in_channels, in_channels // 8, 1)
    self.value_conv = nn.Conv2d(in_channels, in_channels, 1)
    self.gamma = nn.Parameter(torch.zeros(1))

  def forward(self, x):
    proj_query = self.query_conv(x)
    proj_key = self.key_conv(x)
    proj_value = self.value_conv(x)

    energy = _CAWeight.apply(proj_query, proj_key)
    attention = F.softmax(energy, 1)
    out = _CAMap.apply(attention, proj_value)
    out = self.gamma * out + x

    return out


#!<-----------------------------------------------------------------------------
#!< Atrous Spatial Pyramid Pooling
#!<-----------------------------------------------------------------------------


class _ASPPModule(nn.Module):
  def __init__(self, in_channels, out_channels, kernel_size, padding, dilation, batchnorm=nn.BatchNorm2d):
    super(_ASPPModule, self).__init__()
    self.atrous_conv = nn.Conv2d(in_channels,
                                 out_channels,
                                 kernel_size=kernel_size,
                                 stride=1,
                                 padding=padding,
                                 dilation=dilation,
                                 bias=False)
    self.bn = batchnorm(out_channels)
    self.relu = nn.ReLU(True)
    self.reset_parameters()

  def reset_parameters(self):
    for m in self.modules():
      if isinstance(m, nn.Conv2d):
        torch.nn.init.kaiming_normal_(m.weight)
      elif isinstance(m, nn.BatchNorm2d):
        m.weight.data.fill_(1)
        m.bias.data.zero_()

  def forward(self, x):
    x = self.atrous_conv(x)
    x = self.bn(x)
    return self.relu(x)


class AtrousSpatialPyramidPooling(nn.Module):

  r"""ASPP Module: Atrous Spatial Pyramid Pooling

  DeepLab: Semantic Image Segmentation with Deep Convolutional Nets,
    Atrous Convolution, and Fully Connected CRFs. IEEE Transactions on
    Pattern Analysis and Machine Intelligence, 40(4), 834–848.
    https://doi.org/10.1109/TPAMI.2017.2699184

  For backbone:
    drn: in_channels 512
    mobilenet: in_channels 320
    resnet: in_channels 2048

  """

  def __init__(self, in_channels, out_channels=256, output_stride=None, batchnorm=nn.BatchNorm2d):
    super(AtrousSpatialPyramidPooling, self).__init__()

    if output_stride == 16:
      dilations = [1, 6, 12, 18]
    elif output_stride == 8:
      dilations = [1, 12, 24, 36]
    else:
      raise NotImplementedError

    self.aspp1 = _ASPPModule(in_channels, out_channels, kernel_size=1, padding=0,
                             dilation=dilations[0], batchnorm=batchnorm)
    self.aspp2 = _ASPPModule(in_channels, out_channels, kernel_size=3,
                             padding=dilations[1], dilation=dilations[1], batchnorm=batchnorm)
    self.aspp3 = _ASPPModule(in_channels, out_channels, kernel_size=3,
                             padding=dilations[2], dilation=dilations[2], batchnorm=batchnorm)
    self.aspp4 = _ASPPModule(in_channels, out_channels, kernel_size=3,
                             padding=dilations[3], dilation=dilations[3], batchnorm=batchnorm)

    self.global_avg_pool = nn.Sequential(
        nn.AdaptiveAvgPool2d((1, 1)),
        nn.Conv2d(in_channels, out_channels, 1, stride=1, bias=False),
        batchnorm(out_channels),
        nn.ReLU())

    self.conv1 = nn.Conv2d(out_channels * 5, out_channels, 1, bias=False)
    self.bn1 = batchnorm(out_channels)
    self.relu = nn.ReLU()
    self.dropout = nn.Dropout(0.5)
    self.reset_parameters()

  def reset_parameters(self):
    for m in self.modules():
      if isinstance(m, nn.Conv2d):
        torch.nn.init.kaiming_normal_(m.weight)
      elif isinstance(m, nn.BatchNorm2d):
        m.weight.data.fill_(1)
        m.bias.data.zero_()

  def forward(self, x):
    x1 = self.aspp1(x)
    x2 = self.aspp2(x)
    x3 = self.aspp3(x)
    x4 = self.aspp4(x)
    x5 = self.global_avg_pool(x)
    x5 = F.interpolate(x5, size=x4.size()[2:], mode='bilinear', align_corners=True)
    x = torch.cat([x1, x2, x3, x4, x5], dim=1)
    x = self.conv1(x)
    x = self.bn1(x)
    x = self.relu(x)
    return self.dropout(x)

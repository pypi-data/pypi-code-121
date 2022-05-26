# Copyright 2018 The KaiJIN Authors. All Rights Reserved.
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
"""fpn layer bridges backbone network and head

    Impl:
      - FPN
      - RetinaNet
      - SSD Extra

"""
import torch
from torch import nn
from torch.nn import functional as F
import tw

from tw.nn.conv import ConvModule

#!<----------------------------------------------------------------------------
#!< RetinaNet FPN
#!<----------------------------------------------------------------------------


class FpnRetinaNet(nn.Module):
  """RetinaNet use C3, C4, C5, P6, P7

  Args:
      in_channels (List[int]): Number of input channels [C3-C5]
      out_channels (int): Number of output channels [C3-P7 out]
      hidden_channels (int): Number of output channels [C3-P7 out]

  """

  def __init__(self, in_channels, out_channels, hidden_channels, scale_upsample=False, **kwargs):
    super(FpnRetinaNet, self).__init__()
    assert isinstance(in_channels, list)
    assert isinstance(hidden_channels, list)
    assert isinstance(out_channels, list)

    # In some cases, fixing `scale factor` (e.g. 2) is preferred, but it cannot
    #   co-exist with `size` in `F.interpolate`.
    self.scale_upsample = scale_upsample
    num_level = len(in_channels)

    self.lateral_convs = nn.ModuleList()
    self.fpn_convs = nn.ModuleList()

    for ic, oc, hc in zip(in_channels, out_channels[:num_level], hidden_channels):
      l_conv = nn.Conv2d(ic, hc, 1, 1, 0)
      fpn_conv = nn.Conv2d(hc, oc, 3, 1, 1)
      self.lateral_convs.append(ConvModule(l_conv))
      self.fpn_convs.append(ConvModule(fpn_conv))

    # add extra conv layers
    ic = in_channels[-1]
    for oc in out_channels[num_level:]:
      extra_fpn_conv = nn.Conv2d(ic, oc, 3, stride=2, padding=1)
      self.fpn_convs.append(ConvModule(extra_fpn_conv))
      ic = oc

  def forward(self, inputs):
    # build laterals
    laterals = [lateral_conv(inputs[i]) for i, lateral_conv in enumerate(self.lateral_convs)]

    # build top-down path
    for i in range(len(laterals) - 1, 0, -1):
      if self.scale_upsample:
        laterals[i - 1] += F.interpolate(laterals[i], scale_factor=2, mode='nearest')
      else:
        prev_shape = laterals[i - 1].shape[2:]
        laterals[i - 1] += F.interpolate(laterals[i], size=prev_shape, mode='nearest')

    # build outputs from C3 to C5
    outs = [self.fpn_convs[i](laterals[i]) for i in range(len(laterals))]

    # RetinaNet uses feature pyramid levels P3 to P7, where P3 to P5 are computed
    # from the output of the corresponding ResNet residual stage (C3 through C5)
    # using top-down and lateral connections just as in [20], P6 is obtained via
    # a 3×3 stride-2 conv on C5, and P7 is computed by applying ReLU followed
    # by a 3×3 stride-2 conv on P6. This differs slightly from [20]:
    # (1) we don’t use the high-resolution pyramid level P2 for computational reasons,
    # (2) P6 is computed by strided convolution instead of downsampling, and
    # (3) we include P7 to improve large object detection.
    # These minor modifications improve speed while maintaining accuracy.

    # add C5->P6
    outs.append(self.fpn_convs[len(laterals)](inputs[-1]))
    # add P6->P7
    # NOTE: mmdetection does not use ReLU on P6 to P7
    outs.append(self.fpn_convs[-1](outs[-1]))
    return tuple(outs)

#!<----------------------------------------------------------------------------
#!< SSD Extra Layer FPN
#!<----------------------------------------------------------------------------


class FpnSSDExtraLayer(nn.Module):

  def __init__(self, arch, in_channels, out_channels, hidden_channels, kernel_sizes, strides, paddings, **kwargs):
    super(FpnSSDExtraLayer, self).__init__()
    assert arch in ['ssd', 'mssd', 'ssdlite']
    self.arch = arch
    self.in_channels = in_channels
    self.out_channels = out_channels
    self.hidden_channels = hidden_channels
    self.kernel_sizes = kernel_sizes
    self.strides = strides
    self.paddings = paddings

    if self.arch == 'ssd':
      self.l2_norm = tw.nn.L2Norm(kwargs['l2_norm_num'], kwargs['l2_norm_scale'])
      self.extra_layers = self.build_ssd_extra_layer()
    elif self.arch == 'mssd':
      self.extra_layers = self.build_mssd_extra_layer()
    elif self.arch == 'ssdlite':
      self.extra_layers = self.build_ssdlite_extra_layer()
    else:
      raise NotImplementedError

  def build_ssd_extra_layer(self):
    extra_layers = []
    for index in range(len(self.in_channels)):
      if self.hidden_channels[index]:
        ex = nn.Sequential(
            nn.Conv2d(self.in_channels[index],
                      self.hidden_channels[index][0],
                      self.kernel_sizes[index][0],
                      self.strides[index][0],
                      self.paddings[index][0]),
            nn.ReLU(),
            nn.Conv2d(self.hidden_channels[index][0],
                      self.out_channels[index],
                      self.kernel_sizes[index][1],
                      self.strides[index][1],
                      self.paddings[index][1]),
            nn.ReLU(),
        )
        extra_layers.append(ex)
    return nn.ModuleList(extra_layers)

  def build_mssd_extra_layer(self):
    extra_layers = []
    for index in range(len(self.in_channels)):
      if self.hidden_channels[index]:
        ex = nn.Sequential(
            nn.Conv2d(self.in_channels[index],
                      self.hidden_channels[index][0],
                      self.kernel_sizes[index][0],
                      self.strides[index][0],
                      self.paddings[index][0],
                      bias=False),
            nn.BatchNorm2d(self.hidden_channels[index][0]),
            nn.ReLU6(inplace=True),
            nn.Conv2d(self.hidden_channels[index][0],
                      self.out_channels[index],
                      self.kernel_sizes[index][1],
                      self.strides[index][1],
                      self.paddings[index][1],
                      bias=False),
            nn.BatchNorm2d(self.out_channels[index]),
            nn.ReLU6(inplace=True),
        )
        extra_layers.append(ex)
    return nn.ModuleList(extra_layers)

  def build_ssdlite_extra_layer(self):
    extra_layers = []
    for index in range(len(self.in_channels)):
      if self.hidden_channels[index]:
        ex = nn.Sequential(
            nn.Conv2d(self.in_channels[index],
                      self.hidden_channels[index][0],
                      self.kernel_sizes[index][0],
                      self.strides[index][0],
                      self.paddings[index][0],
                      bias=False),
            nn.BatchNorm2d(self.hidden_channels[index][0]),
            nn.ReLU6(inplace=True),
            # dw
            nn.Conv2d(self.hidden_channels[index][0],
                      self.hidden_channels[index][1],
                      self.kernel_sizes[index][1],
                      self.strides[index][1],
                      self.paddings[index][1],
                      groups=self.hidden_channels[index][0],
                      bias=False),
            nn.BatchNorm2d(self.hidden_channels[index][1]),
            nn.ReLU6(inplace=True),
            # pw-linear
            nn.Conv2d(self.hidden_channels[index][1],
                      self.out_channels[index],
                      self.kernel_sizes[index][2],
                      self.strides[index][2],
                      self.paddings[index][2],
                      bias=False),
            nn.BatchNorm2d(self.out_channels[index]),
            nn.ReLU6(inplace=True),
        )
        extra_layers.append(ex)
    return nn.ModuleList(extra_layers)

  def forward(self, inputs):

    outputs = [feat for feat in inputs]

    feature = outputs[-1]
    for layer in self.extra_layers:
      feature = layer(feature)
      outputs.append(feature)

    if hasattr(self, 'l2_norm'):
      outputs[0] = self.l2_norm(outputs[0])

    return tuple(outputs)

#!<----------------------------------------------------------------------------
#!< YOLOF Dilated Encoder FPN
#!<----------------------------------------------------------------------------


class _YOLOFBottleneck(nn.Module):
  """Bottleneck block for DilatedEncoder used in `YOLOF.

      <https://arxiv.org/abs/2103.09460>`.

  The Bottleneck contains three ConvLayers and one residual connection.

  Args:
      in_channels (int): The number of input channels.
      mid_channels (int): The number of middle output channels.
      dilation (int): Dilation rate.

  """

  def __init__(self, in_channels, mid_channels, dilation):
    super(_YOLOFBottleneck, self).__init__()
    self.conv1 = nn.Sequential(
        nn.Conv2d(in_channels, mid_channels, 1),
        nn.BatchNorm2d(mid_channels))
    self.conv2 = nn.Sequential(
        nn.Conv2d(mid_channels, mid_channels, 3, padding=dilation, dilation=dilation),
        nn.BatchNorm2d(mid_channels))
    self.conv3 = nn.Sequential(
        nn.Conv2d(mid_channels, in_channels, 1),
        nn.BatchNorm2d(in_channels))

  def forward(self, x):
    identity = x
    out = self.conv1(x)
    out = self.conv2(out)
    out = self.conv3(out)
    out = out + identity
    return out


class FpnYOLOFDilatedEncoder(nn.Module):

  """Dilated Encoder for YOLOF <https://arxiv.org/abs/2103.09460>`.

  This module contains two types of components:
      - the original FPN lateral convolution layer and fpn convolution layer,
            which are 1x1 conv + 3x3 conv
      - the dilated residual block

  Args:
      in_channels (int): The number of input channels.
      out_channels (int): The number of output channels.
      block_mid_channels (int): The number of middle block output channels
      num_residual_blocks (int): The number of residual blocks.
  """

  def __init__(self, in_channels, out_channels, block_mid_channels, num_residual_blocks, block_dilations=[2, 4, 6, 8]):
    super(FpnYOLOFDilatedEncoder, self).__init__()
    self.in_channels = in_channels
    self.out_channels = out_channels
    self.block_mid_channels = block_mid_channels
    self.num_residual_blocks = num_residual_blocks
    self.block_dilations = block_dilations

    self.lateral_conv = nn.Conv2d(self.in_channels, self.out_channels, kernel_size=1)
    self.lateral_norm = nn.BatchNorm2d(self.out_channels)
    self.fpn_conv = nn.Conv2d(self.out_channels, self.out_channels, kernel_size=3, padding=1)
    self.fpn_norm = nn.BatchNorm2d(self.out_channels)
    encoder_blocks = []
    for i in range(self.num_residual_blocks):
      dilation = self.block_dilations[i]
      encoder_blocks.append(_YOLOFBottleneck(self.out_channels, self.block_mid_channels, dilation=dilation))
    self.dilated_encoder_blocks = nn.Sequential(*encoder_blocks)

  def forward(self, x):
    """ receive C5 feature map
    """
    out = self.lateral_norm(self.lateral_conv(x))
    out = self.fpn_norm(self.fpn_conv(out))
    return self.dilated_encoder_blocks(out)

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
import torch
import torch.nn as nn
import torch.nn.functional as F
from .utils import _ConvBNReLU
from .utils import _ResnetBackbone


class PSANet(nn.Module):
  """Hengshuang Zhao, et al. "PSANet: Point-wise Spatial Attention Network for Scene Parsing." ECCV-2018.
  """

  def __init__(self, num_classes, arch='resnet50', **kwargs):
    super(PSANet, self).__init__()
    self.backbone = _ResnetBackbone(arch, **kwargs)
    self.head = _PSAHead(num_classes, **kwargs)

  def forward(self, x):
    size = x.size()[2:]
    _, _, c3, c4 = self.backbone.forward(x)
    outputs = list()
    x = self.head(c4)
    x = F.interpolate(x, size, mode='bilinear', align_corners=True)
    outputs.append(x)
    return tuple(outputs)


class _PSAHead(nn.Module):
  def __init__(self, num_classes, norm_layer=nn.BatchNorm2d, **kwargs):
    super(_PSAHead, self).__init__()
    # psa_out_channels = crop_size // 8 ** 2
    self.psa = _PointwiseSpatialAttention(2048, 3600, norm_layer)
    self.conv_post = _ConvBNReLU(1024, 2048, 1, norm_layer=norm_layer)
    self.project = nn.Sequential(
        _ConvBNReLU(4096, 512, 3, padding=1, norm_layer=norm_layer),
        nn.Dropout2d(0.1, False),
        nn.Conv2d(512, num_classes, 1))

  def forward(self, x):
    global_feature = self.psa(x)
    out = self.conv_post(global_feature)
    out = torch.cat([x, out], dim=1)
    out = self.project(out)

    return out


class _PointwiseSpatialAttention(nn.Module):
  def __init__(self, in_channels, out_channels, norm_layer=nn.BatchNorm2d, **kwargs):
    super(_PointwiseSpatialAttention, self).__init__()
    reduced_channels = 512
    self.collect_attention = _AttentionGeneration(
        in_channels, reduced_channels, out_channels, norm_layer)
    self.distribute_attention = _AttentionGeneration(
        in_channels, reduced_channels, out_channels, norm_layer)

  def forward(self, x):
    collect_fm = self.collect_attention(x)
    distribute_fm = self.distribute_attention(x)
    psa_fm = torch.cat([collect_fm, distribute_fm], dim=1)
    return psa_fm


class _AttentionGeneration(nn.Module):
  def __init__(self, in_channels, reduced_channels, out_channels, norm_layer, **kwargs):
    super(_AttentionGeneration, self).__init__()
    self.conv_reduce = _ConvBNReLU(
        in_channels, reduced_channels, 1, norm_layer=norm_layer)
    self.attention = nn.Sequential(
        _ConvBNReLU(reduced_channels, reduced_channels,
                    1, norm_layer=norm_layer),
        nn.Conv2d(reduced_channels, out_channels, 1, bias=False))

    self.reduced_channels = reduced_channels

  def forward(self, x):
    reduce_x = self.conv_reduce(x)
    attention = self.attention(reduce_x)
    n, c, h, w = attention.size()
    attention = attention.view(n, c, -1)
    reduce_x = reduce_x.view(n, self.reduced_channels, -1)
    fm = torch.bmm(reduce_x, torch.softmax(attention, dim=1))
    fm = fm.view(n, self.reduced_channels, h, w)

    return fm

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
r"""Segment base if using resnet series"""
import torch
import torch.nn.functional as F
from torch import nn
from tw.models.backbone2d import resnet


class _ConvBNReLU(nn.Module):
  def __init__(self, in_channels, out_channels, kernel_size, stride=1, padding=0,
               dilation=1, groups=1, relu6=False, norm_layer=nn.BatchNorm2d, **kwargs):
    super(_ConvBNReLU, self).__init__()
    self.conv = nn.Conv2d(in_channels, out_channels, kernel_size,
                          stride, padding, dilation, groups, bias=False)
    self.bn = norm_layer(out_channels)
    self.relu = nn.ReLU6(True) if relu6 else nn.ReLU(True)

  def forward(self, x):
    x = self.conv(x)
    x = self.bn(x)
    x = self.relu(x)
    return x


class _ConvBNPReLU(nn.Module):
  def __init__(self, in_channels, out_channels, kernel_size, stride=1, padding=0,
               dilation=1, groups=1, norm_layer=nn.BatchNorm2d, **kwargs):
    super(_ConvBNPReLU, self).__init__()
    self.conv = nn.Conv2d(in_channels, out_channels, kernel_size,
                          stride, padding, dilation, groups, bias=False)
    self.bn = norm_layer(out_channels)
    self.prelu = nn.PReLU(out_channels)

  def forward(self, x):
    x = self.conv(x)
    x = self.bn(x)
    x = self.prelu(x)
    return x


class _ConvBN(nn.Module):
  def __init__(self, in_channels, out_channels, kernel_size, stride=1, padding=0,
               dilation=1, groups=1, norm_layer=nn.BatchNorm2d, **kwargs):
    super(_ConvBN, self).__init__()
    self.conv = nn.Conv2d(in_channels, out_channels, kernel_size,
                          stride, padding, dilation, groups, bias=False)
    self.bn = norm_layer(out_channels)

  def forward(self, x):
    x = self.conv(x)
    x = self.bn(x)
    return x


class _BNPReLU(nn.Module):
  def __init__(self, out_channels, norm_layer=nn.BatchNorm2d, **kwargs):
    super(_BNPReLU, self).__init__()
    self.bn = norm_layer(out_channels)
    self.prelu = nn.PReLU(out_channels)

  def forward(self, x):
    x = self.bn(x)
    x = self.prelu(x)
    return x


class _PSPModule(nn.Module):
  def __init__(self, in_channels, sizes=(1, 2, 3, 6), **kwargs):
    super(_PSPModule, self).__init__()
    out_channels = int(in_channels / 4)
    self.avgpools = nn.ModuleList()
    self.convs = nn.ModuleList()
    for size in sizes:
      self.avgpool.append(nn.AdaptiveAvgPool2d(size))
      self.convs.append(_ConvBNReLU(in_channels, out_channels, 1, **kwargs))

  def forward(self, x):
    size = x.size()[2:]
    feats = [x]
    for (avgpool, conv) in enumerate(zip(self.avgpools, self.convs)):
      feats.append(F.interpolate(conv(avgpool(x)),
                                 size,
                                 mode='bilinear',
                                 align_corners=True))
    return torch.cat(feats, dim=1)


def _ResnetBackbone(arch, **kwargs):
  if arch == 'resnet18':
    backbone = resnet.resnet18(
        output_backbone=True,
        **kwargs)
  elif arch == 'resnet34':
    backbone = resnet.resnet34(
        output_backbone=True,
        **kwargs)
  elif arch == 'resnet50':
    backbone = resnet.resnet50(
        output_backbone=True,
        **kwargs)
  elif arch == 'resnet101':
    backbone = resnet.resnet101(
        output_backbone=True,
        **kwargs)
  elif arch == 'resnet152':
    backbone = resnet.resnet152(
        output_backbone=True,
        **kwargs)
  else:
    raise RuntimeError('unknown arch: {}'.format(arch))
  return backbone

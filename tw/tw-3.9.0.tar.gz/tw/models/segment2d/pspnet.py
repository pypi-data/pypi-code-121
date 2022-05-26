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
"""Pyramid Scene Parsing Network"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from .utils import _ResnetBackbone


class PSPNet(nn.Module):
  def __init__(self, num_classes, arch='resnet50', **kwargs):
    super(PSPNet, self).__init__()
    self.backbone = _ResnetBackbone(arch, **kwargs)
    self.head = _PSPHead(num_classes, **kwargs)

  def forward(self, x):
    size = x.size()[2:]
    _, _, c3, c4 = self.backbone.forward(x)
    outputs = []
    x = self.head(c4)
    x = F.interpolate(x, size, mode='bilinear', align_corners=True)
    outputs.append(x)
    return tuple(outputs)


def _PSP1x1Conv(in_channels, out_channels, norm_layer, norm_kwargs):
  return nn.Sequential(
      nn.Conv2d(in_channels, out_channels, 1, bias=False),
      norm_layer(out_channels, **({} if norm_kwargs is None else norm_kwargs)),
      nn.ReLU(True))


class _PyramidPooling(nn.Module):
  def __init__(self, in_channels, **kwargs):
    super(_PyramidPooling, self).__init__()
    out_channels = int(in_channels / 4)
    self.avgpool1 = nn.AdaptiveAvgPool2d(1)
    self.avgpool2 = nn.AdaptiveAvgPool2d(2)
    self.avgpool3 = nn.AdaptiveAvgPool2d(3)
    self.avgpool4 = nn.AdaptiveAvgPool2d(6)
    self.conv1 = _PSP1x1Conv(in_channels, out_channels, **kwargs)
    self.conv2 = _PSP1x1Conv(in_channels, out_channels, **kwargs)
    self.conv3 = _PSP1x1Conv(in_channels, out_channels, **kwargs)
    self.conv4 = _PSP1x1Conv(in_channels, out_channels, **kwargs)

  def forward(self, x):
    size = x.size()[2:]
    feat1 = F.interpolate(self.conv1(self.avgpool1(x)),
                          size, mode='bilinear', align_corners=True)
    feat2 = F.interpolate(self.conv2(self.avgpool2(x)),
                          size, mode='bilinear', align_corners=True)
    feat3 = F.interpolate(self.conv3(self.avgpool3(x)),
                          size, mode='bilinear', align_corners=True)
    feat4 = F.interpolate(self.conv4(self.avgpool4(x)),
                          size, mode='bilinear', align_corners=True)
    return torch.cat([x, feat1, feat2, feat3, feat4], dim=1)


class _PSPHead(nn.Module):
  def __init__(self, num_classes, norm_layer=nn.BatchNorm2d, norm_kwargs=None, **kwargs):
    super(_PSPHead, self).__init__()
    self.psp = _PyramidPooling(
        2048, norm_layer=norm_layer, norm_kwargs=norm_kwargs)
    self.block = nn.Sequential(
        nn.Conv2d(4096, 512, 3, padding=1, bias=False),
        norm_layer(512, **({} if norm_kwargs is None else norm_kwargs)),
        nn.ReLU(True),
        nn.Dropout(0.1),
        nn.Conv2d(512, num_classes, 1))

  def forward(self, x):
    x = self.psp(x)
    return self.block(x)

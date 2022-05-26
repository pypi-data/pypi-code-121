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
import tw
from .utils import _ResnetBackbone


class CCNet(nn.Module):
  r"""CCNet

  Reference:
      Zilong Huang, et al. "CCNet: Criss-Cross Attention for Semantic Segmentation."
      arXiv preprint arXiv:1811.11721 (2018).
  """

  def __init__(self, num_classes, arch='resnet50', **kwargs):
    super(CCNet, self).__init__()
    self.backbone = _ResnetBackbone(arch, **kwargs)
    self.head = _CCHead(num_classes, **kwargs)

  def forward(self, x):
    size = x.size()[2:]
    _, _, c3, c4 = self.backbone.forward(x)
    outputs = list()
    x = self.head(c4)
    x = F.interpolate(x, size, mode='bilinear', align_corners=True)
    outputs.append(x)
    return tuple(outputs)


class _CCHead(nn.Module):
  def __init__(self, num_classes, norm_layer=nn.BatchNorm2d, **kwargs):
    super(_CCHead, self).__init__()
    self.rcca = _RCCAModule(2048, 512, norm_layer, **kwargs)
    self.out = nn.Conv2d(512, num_classes, 1)

  def forward(self, x):
    x = self.rcca(x)
    x = self.out(x)
    return x


class _RCCAModule(nn.Module):
  def __init__(self, in_channels, out_channels, norm_layer, **kwargs):
    super(_RCCAModule, self).__init__()
    inter_channels = in_channels // 4
    self.conva = nn.Sequential(
        nn.Conv2d(in_channels, inter_channels, 3, padding=1, bias=False),
        norm_layer(inter_channels),
        nn.ReLU(True))
    self.cca = tw.nn.CrissCrossAttention(inter_channels)
    self.convb = nn.Sequential(
        nn.Conv2d(inter_channels, inter_channels, 3, padding=1, bias=False),
        norm_layer(inter_channels),
        nn.ReLU(True))

    self.bottleneck = nn.Sequential(
        nn.Conv2d(in_channels + inter_channels,
                  out_channels, 3, padding=1, bias=False),
        norm_layer(out_channels),
        nn.Dropout2d(0.1))

  def forward(self, x, recurrence=1):
    out = self.conva(x)
    for i in range(recurrence):
      out = self.cca(out)
    out = self.convb(out)
    out = torch.cat([x, out], dim=1)
    out = self.bottleneck(out)

    return out

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
from torch import nn
from torch.nn import functional as F

import tw


class FCN32s(nn.Module):
  """There are some difference from original fcn"""

  def __init__(self,
               num_classes,
               arch='vgg16',
               norm_layer=nn.BatchNorm2d,
               **kwargs):
    super(FCN32s, self).__init__()
    if arch == 'vgg16':
      self.backbone = tw.model.backbone.vgg.vgg16().features
    self.head = _FCNHead(512, num_classes, norm_layer)

  def forward(self, x):
    size = x.size()[2:]
    pool5 = self.backbone(x)
    outputs = []
    out = self.head(pool5)
    out = F.interpolate(out, size, mode='bilinear', align_corners=True)
    outputs.append(out)
    return tuple(outputs)


class FCN16s(nn.Module):
  def __init__(self,
               num_classes,
               arch='vgg16',
               norm_layer=nn.BatchNorm2d,
               **kwargs):
    super(FCN16s, self).__init__()
    if arch == 'vgg16':
      self.backbone = tw.model.backbone.vgg.vgg16().features
    else:
      raise RuntimeError('unknown arch: {}'.format(arch))
    self.pool4 = nn.Sequential(*self.backbone[:24])
    self.pool5 = nn.Sequential(*self.backbone[24:])
    self.head = _FCNHead(512, num_classes, norm_layer)
    self.score_pool4 = nn.Conv2d(512, num_classes, 1)

  def forward(self, x):
    pool4 = self.pool4(x)
    pool5 = self.pool5(pool4)

    outputs = []
    score_fr = self.head(pool5)

    score_pool4 = self.score_pool4(pool4)

    upscore2 = F.interpolate(score_fr, score_pool4.size()[2:], mode='bilinear', align_corners=True)  # nopep8
    fuse_pool4 = upscore2 + score_pool4

    out = F.interpolate(fuse_pool4, x.size()[2:], mode='bilinear', align_corners=True)  # nopep8
    outputs.append(out)

    return tuple(outputs)


class FCN8s(nn.Module):
  def __init__(self,
               num_classes,
               arch='vgg16',
               norm_layer=nn.BatchNorm2d,
               **kwargs):
    super(FCN8s, self).__init__()
    if arch == 'vgg16':
      self.backbone = tw.model.backbone.vgg.vgg16().features
    else:
      raise RuntimeError('unknown backbone: {}'.format(arch))
    self.pool3 = nn.Sequential(*self.backbone[:17])
    self.pool4 = nn.Sequential(*self.backbone[17:24])
    self.pool5 = nn.Sequential(*self.backbone[24:])
    self.head = _FCNHead(512, num_classes, norm_layer)
    self.score_pool3 = nn.Conv2d(256, num_classes, 1)
    self.score_pool4 = nn.Conv2d(512, num_classes, 1)

  def forward(self, x):
    pool3 = self.pool3(x)
    pool4 = self.pool4(pool3)
    pool5 = self.pool5(pool4)

    outputs = []
    score_fr = self.head(pool5)

    score_pool4 = self.score_pool4(pool4)
    score_pool3 = self.score_pool3(pool3)

    upscore2 = F.interpolate(score_fr, score_pool4.size()[2:], mode='bilinear', align_corners=True)  # nopep8
    fuse_pool4 = upscore2 + score_pool4

    upscore_pool4 = F.interpolate(fuse_pool4, score_pool3.size()[2:], mode='bilinear', align_corners=True)  # nopep8
    fuse_pool3 = upscore_pool4 + score_pool3

    out = F.interpolate(fuse_pool3, x.size()[2:], mode='bilinear', align_corners=True)  # nopep8
    outputs.append(out)

    return tuple(outputs)


class _FCNHead(nn.Module):
  def __init__(self, in_channels, channels, norm_layer=nn.BatchNorm2d, **kwargs):
    super(_FCNHead, self).__init__()
    inter_channels = in_channels // 4
    self.block = nn.Sequential(
        nn.Conv2d(in_channels, inter_channels, 3, padding=1, bias=False),
        norm_layer(inter_channels),
        nn.ReLU(inplace=True),
        nn.Dropout(0.1),
        nn.Conv2d(inter_channels, channels, 1))

  def forward(self, x):
    return self.block(x)

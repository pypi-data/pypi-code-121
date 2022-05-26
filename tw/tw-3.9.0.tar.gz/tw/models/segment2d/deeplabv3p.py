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

BatchNorm = nn.SyncBatchNorm


class DeepLabv3pDecoder(nn.Module):
  r"""DeepLab-v3+ Decoder Component
  """

  def __init__(self, num_classes, in_channels, out_channels=256):
    super(DeepLabv3pDecoder, self).__init__()
    self.conv1 = nn.Conv2d(in_channels, 48, 1, bias=False)
    self.bn1 = BatchNorm(48)
    self.relu = nn.ReLU()
    self.last_conv = nn.Sequential(
        nn.Conv2d(in_channels=304,
                  out_channels=out_channels,
                  kernel_size=3,
                  stride=1,
                  padding=1,
                  bias=False),
        BatchNorm(out_channels),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Conv2d(in_channels=out_channels,
                  out_channels=out_channels,
                  kernel_size=3,
                  stride=1,
                  padding=1,
                  bias=False),
        BatchNorm(out_channels),
        nn.ReLU(),
        nn.Dropout(0.1),
        nn.Conv2d(in_channels=out_channels,
                  out_channels=num_classes,
                  kernel_size=1,
                  stride=1))
    self.reset_parameters()

  def reset_parameters(self):
    for m in self.modules():
      if isinstance(m, nn.Conv2d):
        torch.nn.init.kaiming_normal_(m.weight)
      elif isinstance(m, BatchNorm):
        m.weight.data.fill_(1)
        m.bias.data.zero_()
      elif isinstance(m, nn.BatchNorm2d):
        m.weight.data.fill_(1)
        m.bias.data.zero_()

  def forward(self, high_level_feature, low_level_feature):
    r"""Merging low_level_feature and high_level_feature
      e.g.
        low_level_feature: [1, 24, 128, 128] -> out_channels
        high_level_feature: [1, 320, 32, 32] -> out_channels
    """
    low_level_feature = self.conv1(low_level_feature)
    low_level_feature = self.bn1(low_level_feature)
    low_level_feature = self.relu(low_level_feature)

    x = F.interpolate(high_level_feature,
                      size=low_level_feature.size()[2:],
                      mode='bilinear',
                      align_corners=True)
    x = torch.cat([x, low_level_feature], dim=1)
    x = self.last_conv(x)

    return x


class DeepLabV3Plus(nn.Module):
  def __init__(self, arch, num_classes):
    super(DeepLabV3Plus, self).__init__()
    if arch == 'drn':
      output_stride = 8
      low_level_channels = 128
      raise NotImplementedError
    elif arch == 'mobilenet_v2':
      output_stride = 16
      in_channels = 320
      low_level_channels = 24
      self.backbone = tw.model.backbone.mobilenet_v2_deeplab.mobilenet_v2_deeplab(output_stride)  # nopep8
    elif arch == 'resnet101':
      low_level_channels = 256
      in_channels = 2048
      output_stride = 16
      self.backbone = tw.model.backbone.resnets_deeplab.resnet101_deeplab(output_stride)  # nopep8
    else:
      raise NotImplementedError(arch)

    out_channels = 256
    self.aspp = tw.nn.ASPP(in_channels, out_channels, output_stride)
    self.decoder = DeepLabv3pDecoder(num_classes, low_level_channels, out_channels)

  def forward(self, images):
    r"""DeepLab v3+"""
    high_level_feature, low_level_feature = self.backbone(images)
    print(high_level_feature.shape)
    refined_high_level_feature = self.aspp(high_level_feature)
    preds = self.decoder(refined_high_level_feature, low_level_feature)
    preds = F.interpolate(preds,
                          size=images.size()[2:],
                          mode='bilinear',
                          align_corners=True)
    return preds

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
r"""ERFNet
  2080ti: 13.27 ms, 75.35 fps
"""
import torch
from torch import nn
from torch.nn import functional as F

BatchNorm = nn.SyncBatchNorm
# BatchNorm = nn.BatchNorm2d


class NonBottleneck1D(nn.Module):
  r"""Reference:
    "ERFNet: Efficient Residual Factorized ConvNet for Real-Time Semantic Segmentation"
  """

  def __init__(self, in_channels, dropout, dilation):
    r"""NonBottleneck1D

    Arguments:
      in_channels:
      dropout: number of dropout
      dilaton:
    """
    super(NonBottleneck1D, self).__init__()
    self.conv3x1_1 = nn.Conv2d(in_channels,
                               in_channels,
                               (3, 1),
                               stride=1,
                               padding=(1, 0),
                               bias=True)
    self.conv1x3_1 = nn.Conv2d(in_channels, in_channels, (1, 3),
                               stride=1,
                               padding=(0, 1),
                               bias=True)
    self.bn1 = nn.BatchNorm2d(in_channels, eps=1e-03)
    self.conv3x1_2 = nn.Conv2d(in_channels,
                               in_channels, (3, 1),
                               stride=1,
                               padding=(1 * dilation, 0),
                               bias=True,
                               dilation=(dilation, 1))
    self.conv1x3_2 = nn.Conv2d(in_channels,
                               in_channels, (1, 3),
                               stride=1,
                               padding=(0, 1 * dilation),
                               bias=True,
                               dilation=(1, dilation))
    self.bn2 = nn.BatchNorm2d(in_channels, eps=1e-03)
    self.dropout = nn.Dropout2d(dropout)

  def forward(self, inputs):
    output = self.conv3x1_1(inputs)
    output = F.relu(output)
    output = self.conv1x3_1(output)
    output = self.bn1(output)
    output = F.relu(output)
    output = self.conv3x1_2(output)
    output = F.relu(output)
    output = self.conv1x3_2(output)
    output = self.bn2(output)
    if (self.dropout.p != 0):
      output = self.dropout(output)
    return F.relu(output + inputs)


class _DownsamplerBlock(nn.Module):
  def __init__(self, in_channels, out_channels):
    r"""Inspired by ENet of (initial blocks)
    """
    super(_DownsamplerBlock, self).__init__()
    self.conv = nn.Conv2d(in_channels,
                          out_channels - in_channels,
                          (3, 3),
                          stride=2,
                          padding=1,
                          bias=True)
    self.pool = nn.MaxPool2d(2, stride=2)
    self.bn = BatchNorm(out_channels, eps=1e-3)

  def forward(self, inputs):
    output = torch.cat([self.conv(inputs), self.pool(inputs)], 1)
    output = self.bn(output)
    return F.relu(output)


class ERFNetEncoder(nn.Module):
  def __init__(self, num_classes=None):
    super(ERFNetEncoder, self).__init__()
    # 1024x512 -> 512x256
    self.initial_block = _DownsamplerBlock(3, 16)
    self.layers = nn.ModuleList()
    # -> 256x128
    self.layers.append(_DownsamplerBlock(16, 64))
    for x in range(0, 5):  # 5 times
      self.layers.append(NonBottleneck1D(64, 0.1, 1))
      # 128x64
    self.layers.append(_DownsamplerBlock(64, 128))
    for x in range(0, 2):  # 2 times
      self.layers.append(NonBottleneck1D(128, 0.1, 2))
      self.layers.append(NonBottleneck1D(128, 0.1, 4))
      self.layers.append(NonBottleneck1D(128, 0.1, 8))
      self.layers.append(NonBottleneck1D(128, 0.1, 16))
    # only for encoder mode:
    # self.output_conv = nn.Conv2d(128, num_classes, 1, stride=1, padding=0, bias=True)

  def forward(self, inputs):
    output = self.initial_block(inputs)
    for layer in self.layers:
      output = layer(output)
    # output = self.output_conv(output)
    return output


class _UpsampleBlock(nn.Module):
  def __init__(self, in_channels, out_channels):
    super(_UpsampleBlock, self).__init__()
    self.conv = nn.ConvTranspose2d(in_channels, out_channels, 3, stride=2,
                                   padding=1, output_padding=1, bias=True)
    self.bn = BatchNorm(out_channels, eps=1e-3)

  def forward(self, inputs):
    output = self.conv(inputs)
    output = self.bn(output)
    return F.relu(output, inplace=True)


class ERFNetDecoder(nn.Module):
  def __init__(self, num_classes, in_channels=128):
    super(ERFNetDecoder, self).__init__()
    self.layers = nn.ModuleList()
    # 2x
    self.layers.append(_UpsampleBlock(in_channels, 64))
    self.layers.append(NonBottleneck1D(64, 0, 1))
    self.layers.append(NonBottleneck1D(64, 0, 1))
    # 2x
    self.layers.append(_UpsampleBlock(64, 16))
    self.layers.append(NonBottleneck1D(16, 0, 1))
    self.layers.append(NonBottleneck1D(16, 0, 1))
    # 2x
    self.output_conv = nn.ConvTranspose2d(in_channels=16,
                                          out_channels=num_classes,
                                          kernel_size=2,
                                          stride=2,
                                          padding=0,
                                          output_padding=0,
                                          bias=True)

  def forward(self, inputs):
    r"""ERFNet decoder transform inputs from 128x64 -> 1024x512 (8x)"""
    outputs = inputs
    for idx, layer in enumerate(self.layers):
      outputs = layer(outputs)
    outputs = self.output_conv(outputs)
    return outputs


class ERFNet(nn.Module):
  def __init__(self, num_classes, output_encoder=False):
    super(ERFNet, self).__init__()
    self.output_encoder = output_encoder
    self.encoder = ERFNetEncoder(num_classes=num_classes)
    self.decoder = ERFNetDecoder(num_classes=num_classes)

  def forward(self, images):
    features = self.encoder(images)
    preds = self.decoder(features)
    if preds.size()[2:] != images.size()[2:]:
      preds = F.interpolate(preds,
                            size=images.size()[2:],
                            mode='bilinear',
                            align_corners=True)
    if self.output_encoder:
      return features, preds
    else:
      return preds

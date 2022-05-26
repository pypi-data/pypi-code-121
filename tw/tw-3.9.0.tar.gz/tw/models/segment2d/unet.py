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

# from tw.nn import SynchronizedBatchNorm2d

BatchNorm2d = nn.SyncBatchNorm


class DoubleConv(nn.Module):
  """(convolution => [BN] => ReLU) * 2"""

  def __init__(self, in_channels, out_channels):
    super().__init__()
    self.double_conv = nn.Sequential(
        nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
        BatchNorm2d(out_channels),
        nn.ReLU(inplace=True),
        nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
        BatchNorm2d(out_channels),
        nn.ReLU(inplace=True)
    )

  def forward(self, x):
    return self.double_conv(x)


class _UNetDownSample(nn.Module):
  """Downscaling with maxpool then double conv"""

  def __init__(self, in_channels, out_channels):
    super().__init__()
    self.maxpool_conv = nn.Sequential(
        nn.MaxPool2d(2),
        DoubleConv(in_channels, out_channels)
    )

  def forward(self, x):
    return self.maxpool_conv(x)


class _UNetUpSample(nn.Module):
  """Upscaling then double conv"""

  def __init__(self, in_channels, out_channels, bilinear=True):
    super().__init__()
    self.up = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
    self.conv = nn.Sequential(
        nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
        BatchNorm2d(out_channels),
        nn.ReLU(inplace=True),
        nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
        BatchNorm2d(out_channels),
        nn.ReLU(inplace=True))

  def forward(self, x1, x2):
    x1 = self.up(x1)
    # input is CHW
    # diffY = torch.tensor([x2.size()[2] - x1.size()[2]])
    # diffX = torch.tensor([x2.size()[3] - x1.size()[3]])
    # x1 = F.pad(x1, [diffX // 2, diffX - diffX // 2,
    #                 diffY // 2, diffY - diffY // 2])
    # if you have padding issues, see
    # https://github.com/HaiyongJiang/U-Net-Pytorch-Unstructured-Buggy/commit/0e854509c2cea854e247a9c615f175f76fbb2e3a
    # https://github.com/xiaopeng-liao/Pytorch-UNet/commit/8ebac70e633bac59fc22bb5195e513d5832fb3bd
    x = torch.cat([x2, x1], dim=1)
    return self.conv(x)


class UNet(nn.Module):
  def __init__(self, num_classes, in_channels):
    super(UNet, self).__init__()
    self.stem = nn.Sequential(
        nn.Conv2d(in_channels, 64, kernel_size=3, padding=1),
        BatchNorm2d(64),
        nn.ReLU(inplace=True),
        nn.Conv2d(64, 64, kernel_size=3, padding=1),
        BatchNorm2d(64),
        nn.ReLU(inplace=True))
    self.down1 = _UNetDownSample(64, 128)
    self.down2 = _UNetDownSample(128, 256)
    self.down3 = _UNetDownSample(256, 512)
    self.down4 = _UNetDownSample(512, 512)
    self.up1 = _UNetUpSample(1024, 256)
    self.up2 = _UNetUpSample(512, 128)
    self.up3 = _UNetUpSample(256, 64)
    self.up4 = _UNetUpSample(128, 64)
    self.out_conv = nn.Conv2d(64, num_classes, kernel_size=1)

  def forward(self, x):
    x1 = self.stem(x)
    x2 = self.down1(x1)
    x3 = self.down2(x2)
    x4 = self.down3(x3)
    x5 = self.down4(x4)
    x = self.up1(x5, x4)
    x = self.up2(x, x3)
    x = self.up3(x, x2)
    x = self.up4(x, x1)
    logits = self.out_conv(x)
    return logits

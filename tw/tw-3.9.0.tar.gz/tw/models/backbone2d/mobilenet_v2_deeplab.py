# Copyright 2017 The KaiJIN Authors. All Rights Reserved.
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
r"""MobileNet DeepLab
"""
import torch
from torch import nn
from torch.nn import functional as F
import tw

# BatchNorm = nn.BatchNorm2d
BatchNorm = nn.SyncBatchNorm


def _conv(in_channels, out_channels, stride):
  return nn.Sequential(
      nn.Conv2d(in_channels, out_channels, 3, stride, 1, bias=False),
      BatchNorm(out_channels),
      nn.ReLU6(inplace=True))


def _fixed_padding(inputs, kernel_size, dilation):
  kernel_size_effective = kernel_size + (kernel_size - 1) * (dilation - 1)
  pad_total = kernel_size_effective - 1
  pad_beg = pad_total // 2
  pad_end = pad_total - pad_beg
  padded_inputs = F.pad(inputs, (pad_beg, pad_end, pad_beg, pad_end))
  return padded_inputs


class InvertedResidual(nn.Module):
  def __init__(self, in_channels, out_channels, stride, dilation, expand_ratio):
    super(InvertedResidual, self).__init__()
    assert stride in [1, 2]
    self.stride = stride
    hidden_dim = round(in_channels * expand_ratio)
    self.use_res_connect = self.stride == 1 and in_channels == out_channels
    self.dilation = dilation
    self.kernel_size = 3

    if expand_ratio == 1:
      self.conv = nn.Sequential(
          # dw (hidden_dim = in_channels)
          nn.Conv2d(in_channels=in_channels,
                    out_channels=hidden_dim,
                    kernel_size=3,
                    stride=stride,
                    padding=0,
                    dilation=dilation,
                    groups=in_channels,
                    bias=False),
          BatchNorm(hidden_dim),
          nn.ReLU6(inplace=True),
          # pw-linear
          nn.Conv2d(in_channels=hidden_dim,
                    out_channels=out_channels,
                    kernel_size=1,
                    stride=1,
                    padding=0,
                    dilation=1,
                    groups=1,
                    bias=False),
          BatchNorm(out_channels))
    else:
      self.conv = nn.Sequential(
          # pw
          nn.Conv2d(in_channels=in_channels,
                    out_channels=hidden_dim,
                    kernel_size=1,
                    stride=1,
                    padding=0,
                    dilation=1,
                    groups=1,
                    bias=False),
          BatchNorm(hidden_dim),
          nn.ReLU6(inplace=True),
          # dw (hidden_dim = in_channels)
          nn.Conv2d(in_channels=hidden_dim,
                    out_channels=hidden_dim,
                    kernel_size=3,
                    stride=stride,
                    padding=0,
                    dilation=dilation,
                    groups=hidden_dim,
                    bias=False),
          BatchNorm(hidden_dim),
          nn.ReLU6(inplace=True),
          # pw-linear
          nn.Conv2d(in_channels=hidden_dim,
                    out_channels=out_channels,
                    kernel_size=1,
                    stride=1,
                    padding=0,
                    dilation=1,
                    groups=1,
                    bias=False),
          BatchNorm(out_channels))

  def forward(self, x):
    x_pad = _fixed_padding(x, self.kernel_size, dilation=self.dilation)
    if self.use_res_connect:
      x = x + self.conv(x_pad)
    else:
      x = self.conv(x_pad)
    return x


class MobileNetV2(nn.Module):
  def __init__(self, output_stride=8, width_mult=1.):
    super(MobileNetV2, self).__init__()
    block = InvertedResidual
    in_channels = 32
    current_stride = 1
    rate = 1
    inverted_residual_setting = [
        # t, c, n, s
        [1, 16, 1, 1],
        [6, 24, 2, 2],
        [6, 32, 3, 2],
        [6, 64, 4, 2],
        [6, 96, 3, 1],
        [6, 160, 3, 2],
        [6, 320, 1, 1]]

    # building first layer
    in_channels = int(in_channels * width_mult)
    self.features = [_conv(3, in_channels, 2)]
    current_stride *= 2

    # building inverted residual blocks
    for t, c, n, s in inverted_residual_setting:
      if current_stride == output_stride:
        stride = 1
        dilation = rate
        rate *= s
      else:
        stride = s
        dilation = 1
        current_stride *= s

      out_channels = int(c * width_mult)
      for i in range(n):
        if i == 0:
          self.features.append(
              block(in_channels, out_channels, stride, dilation, t))
        else:
          self.features.append(
              block(in_channels, out_channels, 1, dilation, t))
        in_channels = out_channels

    self.features = nn.Sequential(*self.features)
    self.low_level_features = self.features[0:4]
    self.high_level_features = self.features[4:]
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

  def forward(self, x):
    low_level_feature = self.low_level_features(x)
    x = self.high_level_features(low_level_feature)
    return x, low_level_feature


def mobilenet_v2_deeplab(output_stride, width_mult=1.0):
  return MobileNetV2(output_stride=output_stride, width_mult=width_mult)


if __name__ == "__main__":
  input = torch.rand(1, 3, 512, 512)
  model = mobilenet_v2_deeplab(output_stride=16)
  output, low_level_feat = model(input)
  print(output.size())
  print(low_level_feat.size())

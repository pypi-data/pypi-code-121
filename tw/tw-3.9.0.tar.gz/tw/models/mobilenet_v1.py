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
import tw
from torch import nn


class _conv_bn(nn.Module):

  def __init__(self, inp, oup, kernel_size, stride, padding):
    super(_conv_bn, self).__init__()
    self.conv = nn.Sequential(
        nn.Conv2d(inp, oup, kernel_size, stride, padding, bias=False),
        nn.BatchNorm2d(oup),
        nn.ReLU6(inplace=True),
    )
    self.depth = oup

  def forward(self, x):
    return self.conv(x)


class _depth_sepconv(nn.Module):

  def __init__(self, inp, oup, stride):
    super(_depth_sepconv, self).__init__()

    self.conv = nn.Sequential(
        # dw
        nn.Conv2d(inp, inp, 3, stride, 1, groups=inp, bias=False),
        nn.BatchNorm2d(inp),
        nn.ReLU6(inplace=True),
        # pw
        nn.Conv2d(inp, oup, 1, 1, 0, bias=False),
        nn.BatchNorm2d(oup),
        nn.ReLU6(inplace=True),
    )
    self.depth = oup

  def forward(self, x):
    return self.conv(x)


class MobilenetV1(nn.Module):

  def __init__(self, num_classes=1000, depth_multiplier=1.0, min_depth=8, **kwargs):
    super(MobilenetV1, self).__init__()

    self.depth_multiplier = depth_multiplier
    self.min_depth = min_depth

    # define backbone network
    self.depth = lambda d: max(int(d * self.depth_multiplier), self.min_depth)
    self.features = nn.Sequential(*self.builder_backbone())
    # building classifier
    self.classifier = nn.Sequential(
        nn.Dropout(0.2),
        nn.Linear(1024, num_classes))

  def builder_backbone(self):

    # Conv
    layers = [_conv_bn(3, 32, 3, 2, 1)]
    in_channels = 32

    # Residual
    residual_depths = [64, 128, 128, 256, 256,
                       512, 512, 512, 512, 512, 512, 1024, 1024]
    residual_strides = [1, 2, 1, 2, 1, 2, 1, 1, 1, 1, 1, 2, 1]
    for index in range(len(residual_depths)):
      layers += [_depth_sepconv(in_channels, self.depth(
          residual_depths[index]), residual_strides[index])]
      in_channels = self.depth(residual_depths[index])

    return layers

  def reset_parameters(self):
    for m in self.extras.modules():
      if isinstance(m, nn.Conv2d):
        tw.nn.initialize.kaiming(m)

  def forward(self, x):
    for k in range(len(self.features)):
      x = self.features[k](x)
    x = x.mean([2, 3])
    x = self.classifier(x)
    return x


def mobilenet_v1(num_classes=1000):
  return MobilenetV1(num_classes=num_classes)

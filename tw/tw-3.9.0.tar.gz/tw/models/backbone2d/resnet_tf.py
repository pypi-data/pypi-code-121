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
r"""Resnet-Implementation as in tensorflow.
"""
import torch.nn as nn
import math


class Bottleneck(nn.Module):
  def __init__(self, in_planes, map_planes, kind):
    super(Bottleneck, self).__init__()
    self.kind = kind

    if kind == 'first':
      self.preact = nn.Sequential(
          nn.BatchNorm2d(in_planes, momentum=0.003),
          nn.ReLU(inplace=True))
      self.conv1 = nn.Sequential(
          nn.Conv2d(in_planes, map_planes, 1, bias=False),
          nn.BatchNorm2d(map_planes, momentum=0.003),
          nn.ReLU(inplace=True))
      self.conv2 = nn.Sequential(
          nn.Conv2d(map_planes, map_planes, 3, padding=1, bias=False),
          nn.BatchNorm2d(map_planes, momentum=0.003),
          nn.ReLU(inplace=True))
      self.conv3 = nn.Sequential(
          nn.Conv2d(map_planes, map_planes * 4, 1, bias=True))
      self.shortcut = nn.Sequential(
          nn.Conv2d(in_planes, map_planes * 4, 1, bias=True))

    elif kind == 'middle':
      self.preact = nn.Sequential(
          nn.BatchNorm2d(map_planes * 4, momentum=0.003),
          nn.ReLU(inplace=True))
      self.conv1 = nn.Sequential(
          nn.Conv2d(map_planes * 4, map_planes, 1, bias=False),
          nn.BatchNorm2d(map_planes, momentum=0.003),
          nn.ReLU(inplace=True))
      self.conv2 = nn.Sequential(
          nn.Conv2d(map_planes, map_planes, 3, padding=1, bias=False),
          nn.BatchNorm2d(map_planes, momentum=0.003),
          nn.ReLU(inplace=True))
      self.conv3 = nn.Sequential(
          nn.Conv2d(map_planes, map_planes * 4, 1, bias=True))

    else:
      self.preact = nn.Sequential(
          nn.BatchNorm2d(map_planes * 4, momentum=0.003),
          nn.ReLU(inplace=True))
      self.conv1 = nn.Sequential(
          nn.Conv2d(map_planes * 4, map_planes, 1, bias=False),
          nn.BatchNorm2d(map_planes, momentum=0.003),
          nn.ReLU(inplace=True))
      self.conv2 = nn.Sequential(
          nn.Conv2d(map_planes, map_planes, 3, 2, padding=1, bias=False),
          nn.BatchNorm2d(map_planes, momentum=0.003),
          nn.ReLU(inplace=True))
      self.conv3 = nn.Sequential(
          nn.Conv2d(map_planes, map_planes * 4, 1, bias=True))
      self.shortcut = nn.MaxPool2d(kernel_size=1, stride=2, padding=0)

  def forward(self, x):
    if self.kind == 'first':
      preact = self.preact(x)
      net = self.conv1(preact)
      net = self.conv2(net)
      net = self.conv3(net)
      residual = self.shortcut(preact)
      out = net + residual
    elif self.kind == 'middle':
      preact = self.preact(x)
      net = self.conv1(preact)
      net = self.conv2(net)
      net = self.conv3(net)
      out = net + x
    else:
      preact = self.preact(x)
      net = self.conv1(preact)
      net = self.conv2(net)
      net = self.conv3(net)
      residual = self.shortcut(x)
      out = net + residual
    return out


class ResNet(nn.Module):

  def __init__(self, block, layers, num_classes=1000, lower_dim=None):
    self.inplanes = 64
    super(ResNet, self).__init__()

    # root
    self.root = nn.Sequential(
        nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3, bias=True),
        nn.MaxPool2d(kernel_size=3, stride=2, padding=1))

    # blocks
    self.layer1 = self._make_layer(block, 64, 64, layers[0], True)
    self.layer2 = self._make_layer(block, 256, 128, layers[1], True)
    self.layer3 = self._make_layer(block, 512, 256, layers[2], True)
    self.layer4 = self._make_layer(block, 1024, 512, layers[3], False)

    # add lower dims
    if isinstance(lower_dim, int):
      # postbn
      self.postbn = nn.Sequential(
          nn.Conv2d(2048, lower_dim, 1, 1, groups=int(2048 / lower_dim)),
          nn.BatchNorm2d(lower_dim, momentum=0.003),
          # nn.ReLU(inplace=True)) # default
          nn.LeakyReLU(0.2, inplace=True))
      # output
      self.avgpool = nn.AvgPool2d(7, stride=1)
      self.fc = nn.Linear(lower_dim, num_classes)
    else:
      # postbn
      self.postbn = nn.Sequential(
          nn.BatchNorm2d(2048, momentum=0.003),
          nn.ReLU(inplace=True))  # default
      # nn.LeakyReLU(0.2, inplace=True))
      # output
      self.avgpool = nn.AvgPool2d(7, stride=1)
      # self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
      self.fc = nn.Linear(2048, num_classes)

    # endpoints
    self.endpoints = {}

    # init
    for m in self.modules():
      if isinstance(m, nn.Conv2d):
        n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
        m.weight.data.normal_(0, math.sqrt(2. / n))
      elif isinstance(m, nn.BatchNorm2d):
        m.weight.data.fill_(1)
        m.bias.data.zero_()

  def _make_layer(self, block, in_planes, map_planes, nums, downsample):
    layers = []
    for i in range(nums):
      if i == 0:
        kind = 'first'
      elif i == nums - 1 and downsample:
        kind = 'last'
      else:
        kind = 'middle'
      layers.append(block(in_planes, map_planes, kind))
    return nn.Sequential(*layers)

  def forward(self, x):
    x = self.root(x)
    x = self.layer1(x)
    x = self.layer2(x)
    x = self.layer3(x)
    x = self.layer4(x)
    x = self.postbn(x)
    self.endpoints['before_avg'] = x
    x = self.avgpool(x)
    x = x.view(x.size(0), -1)
    self.endpoints['after_avg'] = x
    x = self.fc(x)

    return x


def resnet50(**kwargs):
  """Constructs a ResNet-50 model.

  Args:
      pretrained (bool): If True, returns a model pre-trained on ImageNet
  """
  model = ResNet(Bottleneck, [3, 4, 6, 3], **kwargs)
  return model


def resnet101(**kwargs):
  """Constructs a ResNet-101 model.

  Args:
      pretrained (bool): If True, returns a model pre-trained on ImageNet
  """
  model = ResNet(Bottleneck, [3, 4, 23, 3], **kwargs)
  return model


def resnet152(**kwargs):
  """Constructs a ResNet-152 model.

  Args:
      pretrained (bool): If True, returns a model pre-trained on ImageNet
  """
  model = ResNet(Bottleneck, [3, 8, 36, 3], **kwargs)
  return model

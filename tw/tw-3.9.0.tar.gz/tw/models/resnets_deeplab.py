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
"""ResNets by using deeplab"""
import math
import torch.nn as nn
import torch.utils.model_zoo as model_zoo


BatchNorm = nn.SyncBatchNorm


class Bottleneck(nn.Module):
  expansion = 4

  def __init__(self, inplanes, planes, stride=1, dilation=1, downsample=None):
    super(Bottleneck, self).__init__()
    self.conv1 = nn.Conv2d(inplanes, planes, kernel_size=1, bias=False)
    self.bn1 = BatchNorm(planes)
    self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, stride=stride,
                           dilation=dilation, padding=dilation, bias=False)
    self.bn2 = BatchNorm(planes)
    self.conv3 = nn.Conv2d(planes, planes * 4, kernel_size=1, bias=False)
    self.bn3 = BatchNorm(planes * 4)
    self.relu = nn.ReLU(inplace=True)
    self.downsample = downsample
    self.stride = stride
    self.dilation = dilation

  def forward(self, x):
    residual = x

    out = self.conv1(x)
    out = self.bn1(out)
    out = self.relu(out)

    out = self.conv2(out)
    out = self.bn2(out)
    out = self.relu(out)

    out = self.conv3(out)
    out = self.bn3(out)

    if self.downsample is not None:
      residual = self.downsample(x)

    out += residual
    out = self.relu(out)

    return out


class ResNet(nn.Module):

  def __init__(self, block, layers, output_stride):
    self.inplanes = 64
    super(ResNet, self).__init__()

    blocks = [1, 2, 4]
    if output_stride == 16:
      strides = [1, 2, 2, 1]
      dilations = [1, 1, 1, 2]
    elif output_stride == 8:
      strides = [1, 2, 1, 1]
      dilations = [1, 1, 2, 4]
    else:
      raise NotImplementedError

    # Modules
    self.conv1 = nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3, bias=False)  # nopep8
    self.bn1 = BatchNorm(64)
    self.relu = nn.ReLU(inplace=True)
    self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)

    self.layer1 = self._make_layer(
        block, 64, layers[0], stride=strides[0], dilation=dilations[0])  # nopep8
    self.layer2 = self._make_layer(
        block, 128, layers[1], stride=strides[1], dilation=dilations[1])  # nopep8
    self.layer3 = self._make_layer(
        block, 256, layers[2], stride=strides[2], dilation=dilations[2])  # nopep8
    self.layer4 = self._make_MG_unit(
        block, 512, blocks=blocks, stride=strides[3], dilation=dilations[3])  # nopep8
    self._init_weight()

  def _make_layer(self, block, planes, blocks, stride=1, dilation=1):
    downsample = None
    if stride != 1 or self.inplanes != planes * block.expansion:
      downsample = nn.Sequential(
          nn.Conv2d(self.inplanes, planes * block.expansion,
                    kernel_size=1, stride=stride, bias=False),
          BatchNorm(planes * block.expansion),
      )

    layers = []
    layers.append(block(self.inplanes, planes, stride, dilation, downsample))
    self.inplanes = planes * block.expansion
    for i in range(1, blocks):
      layers.append(block(self.inplanes, planes, dilation=dilation))  # nopep8

    return nn.Sequential(*layers)

  def _make_MG_unit(self, block, planes, blocks, stride=1, dilation=1):
    downsample = None
    if stride != 1 or self.inplanes != planes * block.expansion:
      downsample = nn.Sequential(
          nn.Conv2d(self.inplanes, planes * block.expansion,
                    kernel_size=1, stride=stride, bias=False),
          BatchNorm(planes * block.expansion),
      )

    layers = []
    layers.append(block(self.inplanes, planes, stride, dilation=blocks[0] * dilation, downsample=downsample))  # nopep8
    self.inplanes = planes * block.expansion
    for i in range(1, len(blocks)):
      layers.append(block(self.inplanes, planes, stride=1, dilation=blocks[i] * dilation))  # nopep8

    return nn.Sequential(*layers)

  def forward(self, input):
    x = self.conv1(input)
    x = self.bn1(x)
    x = self.relu(x)
    x = self.maxpool(x)

    x = self.layer1(x)
    low_level_feat = x
    x = self.layer2(x)
    x = self.layer3(x)
    x = self.layer4(x)
    return x, low_level_feat

  def _init_weight(self):
    for m in self.modules():
      if isinstance(m, nn.Conv2d):
        n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
        m.weight.data.normal_(0, math.sqrt(2. / n))
      elif isinstance(m, SynchronizedBatchNorm2d):
        m.weight.data.fill_(1)
        m.bias.data.zero_()
      elif isinstance(m, nn.BatchNorm2d):
        m.weight.data.fill_(1)
        m.bias.data.zero_()


def resnet101_deeplab(output_stride):
  """Constructs a ResNet-101 model.
  Args:
      pretrained (bool): If True, returns a model pre-trained on ImageNet
  """
  model = ResNet(Bottleneck, [3, 4, 23, 3], output_stride)
  return model


if __name__ == "__main__":
  import torch
  model = resnet101_deeplab(output_stride=16)
  input = torch.rand(1, 3, 512, 512)
  output, low_level_feat = model(input)
  print(model)
  print(output.size())
  print(low_level_feat.size())

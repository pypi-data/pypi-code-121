# Copyright 2020 The KaiJIN Authors. All Rights Reserved.
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
r"""PoolNet
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
|            NAME             |       TYPE        |      KERNEL       |            INPUT            |           OUTPUT            |     FLOPs(M)      |      MACs(M)      |     PARAMs(M)     |     Memory(M)     |
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
|      base.vgg16.base.0      |       conv        |      [3, 3]       |      [1, 3, 256, 256]       |      [1, 64, 256, 256]      |    117.440512     |        0.0        |     0.001792      |        0.0        |
|      base.vgg16.base.1      |    activation     |        []         |      [1, 64, 256, 256]      |      [1, 64, 256, 256]      |     4.194304      |        0.0        |        0.0        |        0.0        |
|      base.vgg16.base.2      |       conv        |      [3, 3]       |      [1, 64, 256, 256]      |      [1, 64, 256, 256]      |    2420.113408    |        0.0        |     0.036928      |        0.0        |
|      base.vgg16.base.3      |    activation     |        []         |      [1, 64, 256, 256]      |      [1, 64, 256, 256]      |     4.194304      |        0.0        |        0.0        |        0.0        |
|      base.vgg16.base.4      |      pooling      |        []         |      [1, 64, 256, 256]      |      [1, 64, 128, 128]      |     4.194304      |        0.0        |        0.0        |        0.0        |
|      base.vgg16.base.5      |       conv        |      [3, 3]       |      [1, 64, 128, 128]      |     [1, 128, 128, 128]      |    1210.056704    |        0.0        |     0.073856      |        0.0        |
|      base.vgg16.base.6      |    activation     |        []         |     [1, 128, 128, 128]      |     [1, 128, 128, 128]      |     2.097152      |        0.0        |        0.0        |        0.0        |
|      base.vgg16.base.7      |       conv        |      [3, 3]       |     [1, 128, 128, 128]      |     [1, 128, 128, 128]      |    2418.016256    |        0.0        |     0.147584      |        0.0        |
|      base.vgg16.base.8      |    activation     |        []         |     [1, 128, 128, 128]      |     [1, 128, 128, 128]      |     2.097152      |        0.0        |        0.0        |        0.0        |
|      base.vgg16.base.9      |      pooling      |        []         |     [1, 128, 128, 128]      |      [1, 128, 64, 64]       |     2.097152      |        0.0        |        0.0        |        0.0        |
|     base.vgg16.base.10      |       conv        |      [3, 3]       |      [1, 128, 64, 64]       |      [1, 256, 64, 64]       |    1209.008128    |        0.0        |     0.295168      |        0.0        |
|     base.vgg16.base.11      |    activation     |        []         |      [1, 256, 64, 64]       |      [1, 256, 64, 64]       |     1.048576      |        0.0        |        0.0        |        0.0        |
|     base.vgg16.base.12      |       conv        |      [3, 3]       |      [1, 256, 64, 64]       |      [1, 256, 64, 64]       |    2416.96768     |        0.0        |      0.59008      |        0.0        |
|     base.vgg16.base.13      |    activation     |        []         |      [1, 256, 64, 64]       |      [1, 256, 64, 64]       |     1.048576      |        0.0        |        0.0        |        0.0        |
|     base.vgg16.base.14      |       conv        |      [3, 3]       |      [1, 256, 64, 64]       |      [1, 256, 64, 64]       |    2416.96768     |        0.0        |      0.59008      |        0.0        |
|     base.vgg16.base.15      |    activation     |        []         |      [1, 256, 64, 64]       |      [1, 256, 64, 64]       |     1.048576      |        0.0        |        0.0        |        0.0        |
|     base.vgg16.base.16      |      pooling      |        []         |      [1, 256, 64, 64]       |      [1, 256, 32, 32]       |     1.048576      |        0.0        |        0.0        |        0.0        |
|     base.vgg16.base.17      |       conv        |      [3, 3]       |      [1, 256, 32, 32]       |      [1, 512, 32, 32]       |    1208.48384     |        0.0        |      1.18016      |        0.0        |
|     base.vgg16.base.18      |    activation     |        []         |      [1, 512, 32, 32]       |      [1, 512, 32, 32]       |     0.524288      |        0.0        |        0.0        |        0.0        |
|     base.vgg16.base.19      |       conv        |      [3, 3]       |      [1, 512, 32, 32]       |      [1, 512, 32, 32]       |    2416.443392    |        0.0        |     2.359808      |        0.0        |
|     base.vgg16.base.20      |    activation     |        []         |      [1, 512, 32, 32]       |      [1, 512, 32, 32]       |     0.524288      |        0.0        |        0.0        |        0.0        |
|     base.vgg16.base.21      |       conv        |      [3, 3]       |      [1, 512, 32, 32]       |      [1, 512, 32, 32]       |    2416.443392    |        0.0        |     2.359808      |        0.0        |
|     base.vgg16.base.22      |    activation     |        []         |      [1, 512, 32, 32]       |      [1, 512, 32, 32]       |     0.524288      |        0.0        |        0.0        |        0.0        |
|     base.vgg16.base.23      |      pooling      |        []         |      [1, 512, 32, 32]       |      [1, 512, 16, 16]       |     0.524288      |        0.0        |        0.0        |        0.0        |
|     base.vgg16.base.24      |       conv        |      [3, 3]       |      [1, 512, 16, 16]       |      [1, 512, 16, 16]       |    604.110848     |        0.0        |     2.359808      |        0.0        |
|     base.vgg16.base.25      |    activation     |        []         |      [1, 512, 16, 16]       |      [1, 512, 16, 16]       |     0.131072      |        0.0        |        0.0        |        0.0        |
|     base.vgg16.base.26      |       conv        |      [3, 3]       |      [1, 512, 16, 16]       |      [1, 512, 16, 16]       |    604.110848     |        0.0        |     2.359808      |        0.0        |
|     base.vgg16.base.27      |    activation     |        []         |      [1, 512, 16, 16]       |      [1, 512, 16, 16]       |     0.131072      |        0.0        |        0.0        |        0.0        |
|     base.vgg16.base.28      |       conv        |      [3, 3]       |      [1, 512, 16, 16]       |      [1, 512, 16, 16]       |    604.110848     |        0.0        |     2.359808      |        0.0        |
|     base.vgg16.base.29      |    activation     |        []         |      [1, 512, 16, 16]       |      [1, 512, 16, 16]       |     0.131072      |        0.0        |        0.0        |        0.0        |
|     base.vgg16.base.30      |      pooling      |        []         |      [1, 512, 16, 16]       |      [1, 512, 16, 16]       |     0.131072      |        0.0        |        0.0        |        0.0        |
|        base.ppms.0.0        |      pooling      |        []         |      [1, 512, 16, 16]       |       [1, 512, 1, 1]        |     0.131072      |        0.0        |        0.0        |        0.0        |
|        base.ppms.0.1        |       conv        |      [1, 1]       |       [1, 512, 1, 1]        |       [1, 512, 1, 1]        |     0.262144      |        0.0        |     0.262144      |        0.0        |
|        base.ppms.0.2        |    activation     |        []         |       [1, 512, 1, 1]        |       [1, 512, 1, 1]        |     0.000512      |        0.0        |        0.0        |        0.0        |
|        base.ppms.1.0        |      pooling      |        []         |      [1, 512, 16, 16]       |       [1, 512, 3, 3]        |     0.131072      |        0.0        |        0.0        |        0.0        |
|        base.ppms.1.1        |       conv        |      [1, 1]       |       [1, 512, 3, 3]        |       [1, 512, 3, 3]        |     2.359296      |        0.0        |     0.262144      |        0.0        |
|        base.ppms.1.2        |    activation     |        []         |       [1, 512, 3, 3]        |       [1, 512, 3, 3]        |     0.004608      |        0.0        |        0.0        |        0.0        |
|        base.ppms.2.0        |      pooling      |        []         |      [1, 512, 16, 16]       |       [1, 512, 5, 5]        |     0.131072      |        0.0        |        0.0        |        0.0        |
|        base.ppms.2.1        |       conv        |      [1, 1]       |       [1, 512, 5, 5]        |       [1, 512, 5, 5]        |      6.5536       |        0.0        |     0.262144      |        0.0        |
|        base.ppms.2.2        |    activation     |        []         |       [1, 512, 5, 5]        |       [1, 512, 5, 5]        |      0.0128       |        0.0        |        0.0        |        0.0        |
|       base.ppm_cat.0        |       conv        |      [3, 3]       |      [1, 2048, 16, 16]      |      [1, 512, 16, 16]       |    2415.919104    |        0.0        |     9.437184      |        0.0        |
|       base.ppm_cat.1        |    activation     |        []         |      [1, 512, 16, 16]       |      [1, 512, 16, 16]       |     0.131072      |        0.0        |        0.0        |        0.0        |
|       base.infos.0.0        |       conv        |      [3, 3]       |      [1, 512, 32, 32]       |      [1, 512, 32, 32]       |    2415.919104    |        0.0        |     2.359296      |        0.0        |
|       base.infos.0.1        |    activation     |        []         |      [1, 512, 32, 32]       |      [1, 512, 32, 32]       |     0.524288      |        0.0        |        0.0        |        0.0        |
|       base.infos.1.0        |       conv        |      [3, 3]       |      [1, 512, 64, 64]       |      [1, 256, 64, 64]       |    4831.838208    |        0.0        |     1.179648      |        0.0        |
|       base.infos.1.1        |    activation     |        []         |      [1, 256, 64, 64]       |      [1, 256, 64, 64]       |     1.048576      |        0.0        |        0.0        |        0.0        |
|       base.infos.2.0        |       conv        |      [3, 3]       |     [1, 512, 128, 128]      |     [1, 128, 128, 128]      |    9663.676416    |        0.0        |     0.589824      |        0.0        |
|       base.infos.2.1        |    activation     |        []         |     [1, 128, 128, 128]      |     [1, 128, 128, 128]      |     2.097152      |        0.0        |        0.0        |        0.0        |
|     deep_pool.0.pools.0     |      pooling      |        []         |      [1, 512, 16, 16]       |       [1, 512, 8, 8]        |     0.131072      |        0.0        |        0.0        |        0.0        |
|     deep_pool.0.pools.1     |      pooling      |        []         |      [1, 512, 16, 16]       |       [1, 512, 4, 4]        |     0.131072      |        0.0        |        0.0        |        0.0        |
|     deep_pool.0.pools.2     |      pooling      |        []         |      [1, 512, 16, 16]       |       [1, 512, 2, 2]        |     0.131072      |        0.0        |        0.0        |        0.0        |
|     deep_pool.0.convs.0     |       conv        |      [3, 3]       |       [1, 512, 8, 8]        |       [1, 512, 8, 8]        |    150.994944     |        0.0        |     2.359296      |        0.0        |
|     deep_pool.0.convs.1     |       conv        |      [3, 3]       |       [1, 512, 4, 4]        |       [1, 512, 4, 4]        |     37.748736     |        0.0        |     2.359296      |        0.0        |
|     deep_pool.0.convs.2     |       conv        |      [3, 3]       |       [1, 512, 2, 2]        |       [1, 512, 2, 2]        |     9.437184      |        0.0        |     2.359296      |        0.0        |
|      deep_pool.0.relu       |    activation     |        []         |      [1, 512, 16, 16]       |      [1, 512, 16, 16]       |     0.131072      |        0.0        |        0.0        |        0.0        |
|    deep_pool.0.conv_sum     |       conv        |      [3, 3]       |      [1, 512, 32, 32]       |      [1, 512, 32, 32]       |    2415.919104    |        0.0        |     2.359296      |        0.0        |
|   deep_pool.0.conv_sum_c    |       conv        |      [3, 3]       |      [1, 512, 32, 32]       |      [1, 512, 32, 32]       |    2415.919104    |        0.0        |     2.359296      |        0.0        |
|     deep_pool.1.pools.0     |      pooling      |        []         |      [1, 512, 32, 32]       |      [1, 512, 16, 16]       |     0.524288      |        0.0        |        0.0        |        0.0        |
|     deep_pool.1.pools.1     |      pooling      |        []         |      [1, 512, 32, 32]       |       [1, 512, 8, 8]        |     0.524288      |        0.0        |        0.0        |        0.0        |
|     deep_pool.1.pools.2     |      pooling      |        []         |      [1, 512, 32, 32]       |       [1, 512, 4, 4]        |     0.524288      |        0.0        |        0.0        |        0.0        |
|     deep_pool.1.convs.0     |       conv        |      [3, 3]       |      [1, 512, 16, 16]       |      [1, 512, 16, 16]       |    603.979776     |        0.0        |     2.359296      |        0.0        |
|     deep_pool.1.convs.1     |       conv        |      [3, 3]       |       [1, 512, 8, 8]        |       [1, 512, 8, 8]        |    150.994944     |        0.0        |     2.359296      |        0.0        |
|     deep_pool.1.convs.2     |       conv        |      [3, 3]       |       [1, 512, 4, 4]        |       [1, 512, 4, 4]        |     37.748736     |        0.0        |     2.359296      |        0.0        |
|      deep_pool.1.relu       |    activation     |        []         |      [1, 512, 32, 32]       |      [1, 512, 32, 32]       |     0.524288      |        0.0        |        0.0        |        0.0        |
|    deep_pool.1.conv_sum     |       conv        |      [3, 3]       |      [1, 512, 64, 64]       |      [1, 256, 64, 64]       |    4831.838208    |        0.0        |     1.179648      |        0.0        |
|   deep_pool.1.conv_sum_c    |       conv        |      [3, 3]       |      [1, 256, 64, 64]       |      [1, 256, 64, 64]       |    2415.919104    |        0.0        |     0.589824      |        0.0        |
|     deep_pool.2.pools.0     |      pooling      |        []         |      [1, 256, 64, 64]       |      [1, 256, 32, 32]       |     1.048576      |        0.0        |        0.0        |        0.0        |
|     deep_pool.2.pools.1     |      pooling      |        []         |      [1, 256, 64, 64]       |      [1, 256, 16, 16]       |     1.048576      |        0.0        |        0.0        |        0.0        |
|     deep_pool.2.pools.2     |      pooling      |        []         |      [1, 256, 64, 64]       |       [1, 256, 8, 8]        |     1.048576      |        0.0        |        0.0        |        0.0        |
|     deep_pool.2.convs.0     |       conv        |      [3, 3]       |      [1, 256, 32, 32]       |      [1, 256, 32, 32]       |    603.979776     |        0.0        |     0.589824      |        0.0        |
|     deep_pool.2.convs.1     |       conv        |      [3, 3]       |      [1, 256, 16, 16]       |      [1, 256, 16, 16]       |    150.994944     |        0.0        |     0.589824      |        0.0        |
|     deep_pool.2.convs.2     |       conv        |      [3, 3]       |       [1, 256, 8, 8]        |       [1, 256, 8, 8]        |     37.748736     |        0.0        |     0.589824      |        0.0        |
|      deep_pool.2.relu       |    activation     |        []         |      [1, 256, 64, 64]       |      [1, 256, 64, 64]       |     1.048576      |        0.0        |        0.0        |        0.0        |
|    deep_pool.2.conv_sum     |       conv        |      [3, 3]       |     [1, 256, 128, 128]      |     [1, 128, 128, 128]      |    4831.838208    |        0.0        |     0.294912      |        0.0        |
|   deep_pool.2.conv_sum_c    |       conv        |      [3, 3]       |     [1, 128, 128, 128]      |     [1, 128, 128, 128]      |    2415.919104    |        0.0        |     0.147456      |        0.0        |
|     deep_pool.3.pools.0     |      pooling      |        []         |     [1, 128, 128, 128]      |      [1, 128, 64, 64]       |     2.097152      |        0.0        |        0.0        |        0.0        |
|     deep_pool.3.pools.1     |      pooling      |        []         |     [1, 128, 128, 128]      |      [1, 128, 32, 32]       |     2.097152      |        0.0        |        0.0        |        0.0        |
|     deep_pool.3.pools.2     |      pooling      |        []         |     [1, 128, 128, 128]      |      [1, 128, 16, 16]       |     2.097152      |        0.0        |        0.0        |        0.0        |
|     deep_pool.3.convs.0     |       conv        |      [3, 3]       |      [1, 128, 64, 64]       |      [1, 128, 64, 64]       |    603.979776     |        0.0        |     0.147456      |        0.0        |
|     deep_pool.3.convs.1     |       conv        |      [3, 3]       |      [1, 128, 32, 32]       |      [1, 128, 32, 32]       |    150.994944     |        0.0        |     0.147456      |        0.0        |
|     deep_pool.3.convs.2     |       conv        |      [3, 3]       |      [1, 128, 16, 16]       |      [1, 128, 16, 16]       |     37.748736     |        0.0        |     0.147456      |        0.0        |
|      deep_pool.3.relu       |    activation     |        []         |     [1, 128, 128, 128]      |     [1, 128, 128, 128]      |     2.097152      |        0.0        |        0.0        |        0.0        |
|    deep_pool.3.conv_sum     |       conv        |      [3, 3]       |     [1, 128, 128, 128]      |     [1, 128, 128, 128]      |    2415.919104    |        0.0        |     0.147456      |        0.0        |
|         score.score         |       conv        |      [1, 1]       |     [1, 128, 128, 128]      |      [1, 1, 128, 128]       |     2.113536      |        0.0        |     0.000129      |        0.0        |
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
|             SUM             |                   |        []         |             []              |             []              |    63765.6448     |        0.0        |     52.512705     |        0.0        |
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
import torch.nn as nn
import math
import torch
import numpy as np
import torch.nn.functional as F

from tw.nn import FrozenBatchNorm2d


#!<----------------------------------------------------------------------------
#!< MobileNet-v2
#!<----------------------------------------------------------------------------

class ConvBNReLU(nn.Sequential):
  def __init__(self, in_planes, out_planes, kernel_size=3, stride=1, groups=1):
    padding = (kernel_size - 1) // 2
    super(ConvBNReLU, self).__init__(
        nn.Conv2d(in_planes, out_planes, kernel_size, stride,
                  padding, groups=groups, bias=False),
        FrozenBatchNorm2d(out_planes),
        nn.ReLU6(inplace=True))


class InvertedResidual(nn.Module):
  def __init__(self, inp, oup, stride, expand_ratio):
    super(InvertedResidual, self).__init__()
    self.stride = stride
    assert stride in [1, 2]

    hidden_dim = int(round(inp * expand_ratio))
    self.use_res_connect = self.stride == 1 and inp == oup

    layers = []

    # pw
    if expand_ratio != 1:
      layers.append(ConvBNReLU(inp, hidden_dim, kernel_size=1))

    layers.extend([
        # dw
        ConvBNReLU(hidden_dim, hidden_dim, stride=stride, groups=hidden_dim),  # nopep8
        # pw-linear
        nn.Conv2d(hidden_dim, oup, 1, 1, 0, bias=False),
        FrozenBatchNorm2d(oup),
    ])

    self.conv = nn.Sequential(*layers)

  def forward(self, x):
    if self.use_res_connect:
      return x + self.conv(x)
    else:
      return self.conv(x)


class MobileNetV2(nn.Module):
  def __init__(self, num_classes=1000, width_mult=1.0):
    super(MobileNetV2, self).__init__()
    block = InvertedResidual
    input_channel = 32
    last_channel = 1280
    inverted_residual_setting = [
        # t, c, n, s
        [1, 16, 1, 1],
        [6, 24, 2, 2],
        [6, 32, 3, 2],
        [6, 64, 4, 2],
        [6, 96, 3, 1],
        [6, 160, 3, 1],
        [6, 320, 1, 1],
    ]

    # building first layer
    input_channel = int(input_channel * width_mult)
    self.last_channel = int(last_channel * max(1.0, width_mult))
    features = [ConvBNReLU(3, input_channel, stride=2)]

    # building inverted residual blocks
    for t, c, n, s in inverted_residual_setting:
      output_channel = int(c * width_mult)
      for i in range(n):
        stride = s if i == 0 else 1
        features.append(block(input_channel, output_channel, stride, expand_ratio=t))  # nopep8
        input_channel = output_channel

    # building last several layers
    features.append(ConvBNReLU(input_channel, self.last_channel, kernel_size=1))  # nopep8

    # make it nn.Sequential
    self.features = nn.ModuleList(features)

  def forward(self, x):
    xs = []
    for i, f in enumerate(self.features):
      x = f(x)
      if i in [1, 3, 6, 13, 18]:
        xs.append(x)

    # xs output
    # [1, 16, 128, 128]
    # [1, 24, 64, 64]
    # [1, 32, 32, 32]
    # [1, 96, 16, 16]
    # [1, 1280, 16, 16]

    return xs


class MobileNetv2Locate(nn.Module):
  def __init__(self):
    super(MobileNetv2Locate, self).__init__()
    self.backbone = MobileNetV2()

    self.in_planes = 128
    # inverse backbone output
    self.out_planes = [128, 64, 64, 32]

    # backbone last layer
    self.ppms_pre = nn.Conv2d(1280, self.in_planes, 1, 1, bias=False)
    ppms, infos = [], []

    for ii in [1, 3, 5]:
      ppms.append(nn.Sequential(
          nn.AdaptiveAvgPool2d(ii),
          nn.Conv2d(self.in_planes, self.in_planes, 1, 1, bias=False),
          nn.ReLU(inplace=True)))
    self.ppms = nn.ModuleList(ppms)

    self.ppm_cat = nn.Sequential(
        nn.Conv2d(self.in_planes * 4, self.in_planes, 3, 1, 1, bias=False),
        nn.ReLU(inplace=True))

    for ii in self.out_planes:
      infos.append(nn.Sequential(
          nn.Conv2d(self.in_planes, ii, 3, 1, 1, bias=False),
          nn.ReLU(inplace=True)))

    self.infos = nn.ModuleList(infos)

  def forward(self, x):
    x_size = x.size()[2:]
    xs = self.backbone(x)

    xs_1 = self.ppms_pre(xs[-1])
    xls = [xs_1]
    for k in range(len(self.ppms)):
      xls.append(F.interpolate(self.ppms[k](xs_1), xs_1.size()[2:], mode='bilinear', align_corners=True))  # nopep8
    xls = self.ppm_cat(torch.cat(xls, dim=1))

    infos = []
    for k in range(len(self.infos)):
      infos.append(self.infos[k](F.interpolate(xls, xs[len(self.infos) - 1 - k].size()[2:], mode='bilinear', align_corners=True)))  # nopep8

    return xs, infos


def mobilenet_v2_locate():
  model = MobileNetv2Locate()
  return model

#!<----------------------------------------------------------------------------
#!< ResNet-50
#!<----------------------------------------------------------------------------


def conv3x3(in_planes, out_planes, stride=1):
  return nn.Conv2d(in_planes, out_planes, kernel_size=3, stride=stride, padding=1, bias=False)  # nopep8


class BasicBlock(nn.Module):
  expansion = 1

  def __init__(self, inplanes, planes, stride=1, downsample=None):
    super(BasicBlock, self).__init__()
    self.conv1 = conv3x3(inplanes, planes, stride)
    self.bn1 = FrozenBatchNorm2d(planes)
    self.relu = nn.ReLU(inplace=True)
    self.conv2 = conv3x3(planes, planes)
    self.bn2 = FrozenBatchNorm2d(planes)
    self.downsample = downsample
    self.stride = stride

  def forward(self, x):
    residual = x

    out = self.conv1(x)
    out = self.bn1(out)
    out = self.relu(out)

    out = self.conv2(out)
    out = self.bn2(out)

    if self.downsample is not None:
      residual = self.downsample(x)

    out += residual
    out = self.relu(out)

    return out


class Bottleneck(nn.Module):
  expansion = 4

  def __init__(self, inplanes, planes, stride=1, dilation_=1, downsample=None):
    super(Bottleneck, self).__init__()
    self.conv1 = nn.Conv2d(inplanes, planes, kernel_size=1,
                           stride=stride, bias=False)  # change
    self.bn1 = FrozenBatchNorm2d(planes)
    padding = 1
    if dilation_ == 2:
      padding = 2
    elif dilation_ == 4:
      padding = 4
    self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, stride=1,  # change
                           padding=padding, bias=False, dilation=dilation_)
    self.bn2 = FrozenBatchNorm2d(planes)
    self.conv3 = nn.Conv2d(planes, planes * 4, kernel_size=1, bias=False)
    self.bn3 = FrozenBatchNorm2d(planes * 4)
    self.relu = nn.ReLU(inplace=True)
    self.downsample = downsample
    self.stride = stride

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
  def __init__(self, block, layers):
    self.inplanes = 64
    super(ResNet, self).__init__()
    self.conv1 = nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3, bias=False)  # nopep8
    self.bn1 = FrozenBatchNorm2d(64)
    self.relu = nn.ReLU(inplace=True)
    self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1, ceil_mode=True)  # change # nopep8
    self.layer1 = self._make_layer(block, 64, layers[0])
    self.layer2 = self._make_layer(block, 128, layers[1], stride=2)
    self.layer3 = self._make_layer(block, 256, layers[2], stride=2)
    self.layer4 = self._make_layer(block, 512, layers[3], stride=1, dilation__=2)  # nopep8

  def _make_layer(self, block, planes, blocks, stride=1, dilation__=1):
    downsample = None
    if stride != 1 or self.inplanes != planes * block.expansion or dilation__ == 2 or dilation__ == 4:
      downsample = nn.Sequential(
          nn.Conv2d(self.inplanes, planes * block.expansion, kernel_size=1, stride=stride, bias=False),  # nopep8
          FrozenBatchNorm2d(planes * block.expansion),
      )
    layers = []
    layers.append(block(self.inplanes, planes, stride, dilation_=dilation__, downsample=downsample))  # nopep8
    self.inplanes = planes * block.expansion
    for i in range(1, blocks):
      layers.append(block(self.inplanes, planes, dilation_=dilation__))

    return nn.Sequential(*layers)

  def forward(self, x):
    tmp_x = []
    x = self.conv1(x)
    x = self.bn1(x)
    x = self.relu(x)
    tmp_x.append(x)
    x = self.maxpool(x)

    x = self.layer1(x)
    tmp_x.append(x)
    x = self.layer2(x)
    tmp_x.append(x)
    x = self.layer3(x)
    tmp_x.append(x)
    x = self.layer4(x)
    tmp_x.append(x)

    return tmp_x


class ResNetLocate(nn.Module):
  def __init__(self, block, layers):
    super(ResNetLocate, self).__init__()
    self.resnet = ResNet(block, layers)
    self.in_planes = 512
    self.out_planes = [512, 256, 256, 128]

    self.ppms_pre = nn.Conv2d(2048, self.in_planes, 1, 1, bias=False)
    ppms, infos = [], []

    for ii in [1, 3, 5]:
      ppms.append(nn.Sequential(
          nn.AdaptiveAvgPool2d(ii),
          nn.Conv2d(self.in_planes, self.in_planes, 1, 1, bias=False),
          nn.ReLU(inplace=True)))
    self.ppms = nn.ModuleList(ppms)

    self.ppm_cat = nn.Sequential(
        nn.Conv2d(self.in_planes * 4, self.in_planes, 3, 1, 1, bias=False),
        nn.ReLU(inplace=True))

    for ii in self.out_planes:
      infos.append(nn.Sequential(
          nn.Conv2d(self.in_planes, ii, 3, 1, 1, bias=False),
          nn.ReLU(inplace=True)))

    self.infos = nn.ModuleList(infos)

  def forward(self, x):
    x_size = x.size()[2:]
    xs = self.resnet(x)

    xs_1 = self.ppms_pre(xs[-1])
    xls = [xs_1]
    for k in range(len(self.ppms)):
      xls.append(F.interpolate(self.ppms[k](xs_1), xs_1.size()[2:], mode='bilinear', align_corners=True))  # nopep8
    xls = self.ppm_cat(torch.cat(xls, dim=1))

    infos = []
    for k in range(len(self.infos)):
      infos.append(self.infos[k](F.interpolate(xls, xs[len(self.infos) - 1 - k].size()[2:], mode='bilinear', align_corners=True)))  # nopep8

    return xs, infos


def resnet50_locate():
  model = ResNetLocate(Bottleneck, [3, 4, 6, 3])
  return model

#!<----------------------------------------------------------------------------
#!< VGG16
#!<----------------------------------------------------------------------------


def vgg(cfg, i, batch_norm=False):
  layers = []
  in_channels = i
  stage = 1
  for v in cfg:
    if v == 'M':
      stage += 1
      if stage == 6:
        layers += [nn.MaxPool2d(kernel_size=3, stride=1, padding=1)]
      else:
        layers += [nn.MaxPool2d(kernel_size=3, stride=2, padding=1)]
    else:
      if stage == 6:
        conv2d = nn.Conv2d(in_channels, v, kernel_size=3, padding=1)
      else:
        conv2d = nn.Conv2d(in_channels, v, kernel_size=3, padding=1)
      if batch_norm:
        layers += [conv2d, FrozenBatchNorm2d(v), nn.ReLU(inplace=True)]
      else:
        layers += [conv2d, nn.ReLU(inplace=True)]
      in_channels = v
  return layers


class vgg16(nn.Module):
  def __init__(self):
    super(vgg16, self).__init__()
    self.cfg = {'tun': [64, 64, 'M', 128, 128, 'M', 256, 256, 256, 'M', 512, 512, 512, 'M', 512, 512, 512, 'M'], 'tun_ex': [512, 512, 512]}  # nopep8
    self.extract = [8, 15, 22, 29]  # [3, 8, 15, 22, 29]
    self.base = nn.ModuleList(vgg(self.cfg['tun'], 3))

  def forward(self, x):
    tmp_x = []
    for k in range(len(self.base)):
      x = self.base[k](x)
      if k in self.extract:
        tmp_x.append(x)
    return tmp_x


class vgg16_locate(nn.Module):
  def __init__(self):
    super(vgg16_locate, self).__init__()
    self.vgg16 = vgg16()
    self.in_planes = 512
    self.out_planes = [512, 256, 128]

    ppms, infos = [], []
    for ii in [1, 3, 5]:
      ppms.append(nn.Sequential(
          nn.AdaptiveAvgPool2d(ii),
          nn.Conv2d(self.in_planes, self.in_planes, 1, 1, bias=False),
          nn.ReLU(inplace=True)))
    self.ppms = nn.ModuleList(ppms)

    self.ppm_cat = nn.Sequential(
        nn.Conv2d(self.in_planes * 4, self.in_planes, 3, 1, 1, bias=False),
        nn.ReLU(inplace=True))

    for ii in self.out_planes:
      infos.append(nn.Sequential(
          nn.Conv2d(self.in_planes, ii, 3, 1, 1, bias=False),
          nn.ReLU(inplace=True)))

    self.infos = nn.ModuleList(infos)

  def forward(self, x):
    x_size = x.size()[2:]
    xs = self.vgg16(x)

    xls = [xs[-1]]
    for k in range(len(self.ppms)):
      xls.append(F.interpolate(self.ppms[k](xs[-1]), xs[-1].size()[2:], mode='bilinear', align_corners=True))  # nopep8
    xls = self.ppm_cat(torch.cat(xls, dim=1))

    infos = []
    for k in range(len(self.infos)):
      infos.append(self.infos[k](F.interpolate(xls, xs[len(self.infos) - 1 - k].size()[2:], mode='bilinear', align_corners=True)))  # nopep8

    return xs, infos

#!<----------------------------------------------------------------------------
#!< PoolNet
#!<----------------------------------------------------------------------------


config_vgg = {
  'convert': [[128, 256, 512, 512, 512], [64, 128, 256, 512, 512]],
  'deep_pool': [[512, 512, 256, 128], [512, 256, 128, 128], [True, True, True, False], [True, True, True, False]],
  'score': 128,
}  # nopep8

config_resnet = {
  'convert': [[64, 256, 512, 1024, 2048], [128, 256, 256, 512, 512]],
  'deep_pool': [[512, 512, 256, 256, 128], [512, 256, 256, 128, 128], [False, True, True, True, False], [True, True, True, True, False]],
  'score': 128,
}  # nopep8

config_mobilenet_v2 = {
  'convert': [[16, 24, 32, 96, 1280], [32, 64, 64, 128, 128]],
  'deep_pool': [[128, 128, 64, 64, 32], [128, 64, 64, 32, 32], [False, True, True, True, False], [True, True, True, True, False]],
  'score': 32,
}  # nopep8


class ConvertLayer(nn.Module):
  def __init__(self, list_k):
    super(ConvertLayer, self).__init__()
    up = []
    for i in range(len(list_k[0])):
      up.append(nn.Sequential(
          nn.Conv2d(list_k[0][i], list_k[1][i], 1, 1, bias=False),
          nn.ReLU(inplace=True)
      ))
    self.convert0 = nn.ModuleList(up)

  def forward(self, list_x):
    resl = []
    for i in range(len(list_x)):
      resl.append(self.convert0[i](list_x[i]))
    return resl


class DeepPoolLayer(nn.Module):
  def __init__(self, k, k_out, need_x2, need_fuse):
    super(DeepPoolLayer, self).__init__()
    self.pools_sizes = [2, 4, 8]
    self.need_x2 = need_x2
    self.need_fuse = need_fuse
    pools, convs = [], []
    for i in self.pools_sizes:
      pools.append(nn.AvgPool2d(kernel_size=i, stride=i))
      convs.append(nn.Conv2d(k, k, 3, 1, 1, bias=False))
    self.pools = nn.ModuleList(pools)
    self.convs = nn.ModuleList(convs)
    self.relu = nn.ReLU()
    self.conv_sum = nn.Conv2d(k, k_out, 3, 1, 1, bias=False)
    if self.need_fuse:
      self.conv_sum_c = nn.Conv2d(k_out, k_out, 3, 1, 1, bias=False)

  def forward(self, x, x2=None, x3=None):
    x_size = x.size()
    resl = x
    for i in range(len(self.pools_sizes)):
      y = self.convs[i](self.pools[i](x))
      resl = torch.add(resl, F.interpolate(y, x_size[2:], mode='bilinear', align_corners=True))  # nopep8
    resl = self.relu(resl)
    if self.need_x2:
      resl = F.interpolate(resl, x2.size()[2:], mode='bilinear', align_corners=True)  # nopep8
    resl = self.conv_sum(resl)
    if self.need_fuse:
      resl = self.conv_sum_c(torch.add(torch.add(resl, x2), x3))
    return resl


class ScoreLayer(nn.Module):
  def __init__(self, k):
    super(ScoreLayer, self).__init__()
    self.score = nn.Conv2d(k, 1, 1, 1)

  def forward(self, x, x_size=None):
    x = self.score(x)
    if x_size is not None:
      x = F.interpolate(x, x_size[2:], mode='bilinear', align_corners=True)
    return x


def extra_layer(base_model_cfg, locate):
  if base_model_cfg == 'vgg':
    config = config_vgg
  elif base_model_cfg == 'resnet':
    config = config_resnet
  elif base_model_cfg == 'mobilenet_v2':
    config = config_mobilenet_v2

  convert_layers, deep_pool_layers, score_layers = [], [], []
  convert_layers = ConvertLayer(config['convert'])

  for i in range(len(config['deep_pool'][0])):
    deep_pool_layers += [DeepPoolLayer(config['deep_pool'][0][i], config['deep_pool'][1][i], config['deep_pool'][2][i], config['deep_pool'][3][i])]  # nopep8

  score_layers = ScoreLayer(config['score'])

  return locate, convert_layers, deep_pool_layers, score_layers


class PoolNet(nn.Module):
  def __init__(self, base_model_cfg, base, convert_layers, deep_pool_layers, score_layers):
    super(PoolNet, self).__init__()
    self.base_model_cfg = base_model_cfg
    self.base = base
    self.deep_pool = nn.ModuleList(deep_pool_layers)
    self.score = score_layers

    if self.base_model_cfg in ['resnet', 'mobilenet_v2']:
      self.convert = convert_layers

  def forward(self, x):
    x_size = x.size()

    conv2merge, infos = self.base(x)
    if self.base_model_cfg in ['resnet', 'mobilenet_v2']:
      conv2merge = self.convert(conv2merge)
    conv2merge = conv2merge[::-1]

    edge_merge = []
    merge = self.deep_pool[0](conv2merge[0], conv2merge[1], infos[0])
    for k in range(1, len(conv2merge) - 1):
      merge = self.deep_pool[k](merge, conv2merge[k + 1], infos[k])

    merge = self.deep_pool[-1](merge)
    merge = self.score(merge, x_size)
    return merge


def poolnet(base_model_cfg='resnet'):
  if base_model_cfg == 'vgg':
    return PoolNet(base_model_cfg, *extra_layer(base_model_cfg, vgg16_locate()))
  elif base_model_cfg == 'resnet':
    return PoolNet(base_model_cfg, *extra_layer(base_model_cfg, resnet50_locate()))
  elif base_model_cfg == 'mobilenet_v2':
    return PoolNet(base_model_cfg, *extra_layer(base_model_cfg, mobilenet_v2_locate()))


def weights_init(m):
  if isinstance(m, nn.Conv2d):
    m.weight.data.normal_(0, 0.01)
    if m.bias is not None:
      m.bias.data.zero_()


if __name__ == "__main__":
  from tw.utils import flops
  model = poolnet('mobilenet_v2').cuda()
  for k, v in model.state_dict().items():
    print(k, v.shape)
  # model = ResNet(Bottleneck, [3, 4, 6, 3]).cuda()
  # model = MobileNetv2Locate().cuda()
  flops.register(model)
  inputs = torch.rand(1, 3, 160, 320).cuda()
  model.eval()
  with torch.no_grad():
    outputs = model(inputs)

  print(flops.accumulate(model))
  print(outputs.shape)
  flops.unregister(model)

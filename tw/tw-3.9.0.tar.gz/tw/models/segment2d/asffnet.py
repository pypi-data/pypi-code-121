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
r"""ASFFNet

Reference:
  Li, Xiaoming, Wenyu Li, Dongwei Ren, Hongzhi Zhang, Meng Wang, and Wangmeng Zuo.
  “Enhanced Blind Face Restoration With Multi-Exemplar Images and Adaptive Spatial Feature Fusion.”
  In 2020 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR),
  2703–12. Seattle, WA, USA: IEEE, 2020. https://doi.org/10.1109/CVPR42600.2020.00278.

"""
from torch import nn


class _ResBlock(nn.Module):
  def __init__(self, channel, kernel, stride, dilation):
    super(_ResBlock, self).__init__()
    self.block = nn.Sequential(
        nn.Conv2d(channel, channel, kernel, stride,
                  dilation, dilation=dilation),
        nn.BatchNorm2d(channel),
        nn.LeakyReLU(0.2),
        nn.Conv2d(channel, channel, kernel, stride,
                  dilation, dilation=dilation),
    )

  def forward(self, x):
    return x + self.block(x)


class ASFFNet(nn.Module):
  def __init__(self):
    super(ASFFNet, self).__init__()

    # * feature extractor /4
    self.enc1 = nn.Sequential(
        nn.Conv2d(3, 64, 3, 1, 1),
        nn.BatchNorm2d(64),
        nn.LeakyReLU(0.2))
    self.enc1_1 = _ResBlock(64, 3, 1, 7)
    self.enc1_2 = _ResBlock(64, 3, 1, 5)

    self.enc2 = nn.Sequential(
        nn.Conv2d(64, 128, 3, 2, 1),
        nn.BatchNorm2d(128),
        nn.LeakyReLU(0.2))
    self.enc2_1 = _ResBlock(128, 3, 1, 5)
    self.enc2_2 = _ResBlock(128, 3, 1, 3)

    self.enc3 = nn.Sequential(
        nn.Conv2d(128, 128, 3, 2, 1),
        nn.BatchNorm2d(128),
        nn.LeakyReLU(0.2))
    self.enc3_1 = _ResBlock(128, 3, 1, 3)
    self.enc3_2 = _ResBlock(128, 3, 1, 1)

    self.enc4 = nn.Sequential(
        nn.Conv2d(128, 128, 3, 1, 1),
        nn.LeakyReLU(0.2))

    # * reconstruction
    self.dec1 = nn.Conv2d(128, 256, 3, 1, 1)
    self.dec1_1 = _ResBlock(256, 3, 1, 1)
    self.dec1_2 = _ResBlock(256, 3, 1, 1)
    self.dec1_shuffle = nn.PixelShuffle(2)

    self.dec2 = nn.Conv2d(64, 128, 3, 1, 1)
    self.dec2_1 = _ResBlock(128, 3, 1, 1)
    self.dec2_2 = _ResBlock(128, 3, 1, 1)
    self.dec2_shuffle = nn.PixelShuffle(2)

    self.dec3 = nn.Conv2d(32, 32, 3, 1, 1)
    self.dec3_1 = _ResBlock(32, 3, 1, 1)
    self.dec3_2 = _ResBlock(32, 3, 1, 1)

    self.dec4 = nn.Sequential(nn.Conv2d(32, 3, 3, 1, 1))

  def forward(self, x):
    x = self.enc1(x)
    x = self.enc1_1(x)
    x = self.enc1_2(x)
    x = self.enc2(x)
    x = self.enc2_1(x)
    x = self.enc2_2(x)
    x = self.enc3(x)
    x = self.enc3_1(x)
    x = self.enc3_2(x)
    x = self.enc4(x)
    x = self.dec1(x)
    x = self.dec1_1(x)
    x = self.dec1_2(x)
    x = self.dec1_shuffle(x)
    x = self.dec2(x)
    x = self.dec2_1(x)
    x = self.dec2_2(x)
    x = self.dec2_shuffle(x)
    x = self.dec3(x)
    x = self.dec3_1(x)
    x = self.dec3_2(x)
    x = self.dec4(x)
    return x


if __name__ == "__main__":
  from tw.utils import flops
  _net = ASFFNet().eval()
  print(flops.get_model_complexity_info(_net, (3, 128, 128)))

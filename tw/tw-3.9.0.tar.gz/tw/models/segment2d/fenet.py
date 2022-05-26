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
r"""Facial Enhancement Network"""

import torch
from torch import nn
import tw


#!<----------------------------------------------------------------------------
#!< FENet Base
#!<----------------------------------------------------------------------------


class Scale(nn.Module):
  def __init__(self, in_channels):
    super(Scale, self).__init__()
    self.weight = nn.Parameter(torch.ones(in_channels), requires_grad=True)

  def forward(self, x):
    return self.weight.reshape(1, -1, 1, 1) * x


class IMDBModule(nn.Module):
  def __init__(self, channels, mask=None):
    super(IMDBModule, self).__init__()
    assert channels % 4 == 0
    self.small = channels // 4
    self.large = self.small * 3
    self.conv1 = nn.Sequential(nn.Conv2d(channels, channels, 3, 1, 1), nn.ReLU())  # nopep8
    self.conv2 = nn.Sequential(nn.Conv2d(self.large, channels, 3, 1, 1), nn.ReLU())  # nopep8
    self.conv3 = nn.Sequential(nn.Conv2d(self.large, channels, 3, 1, 1), nn.ReLU())  # nopep8
    self.conv4 = nn.Sequential(nn.Conv2d(self.large, self.small, 3, 1, 1), nn.ReLU())  # nopep8
    self.conv5 = nn.Conv2d(channels, channels, 1, 1, 0)

  def forward(self, x):
    d1, r1 = torch.split(self.conv1(x), (self.small, self.large), dim=1)
    d2, r2 = torch.split(self.conv2(r1), (self.small, self.large), dim=1)
    d3, r3 = torch.split(self.conv3(r2), (self.small, self.large), dim=1)
    d4 = self.conv4(r3)
    res = self.conv5(torch.cat((d1, d2, d3, d4), dim=1))
    return x + res


class ResidualBlock(nn.Module):
  def __init__(self, channels, mask='IN'):
    super(ResidualBlock, self).__init__()
    if mask == 'IN':
      self.conv = nn.Sequential(
          nn.Conv2d(channels, channels, 3, 1, 1),
          nn.InstanceNorm2d(channels),
          nn.ReLU(inplace=True),
          nn.Conv2d(channels, channels, 3, 1, 1))
    elif mask == 'SCALE':
      self.conv = nn.Sequential(
          nn.Conv2d(channels, channels, 3, 1, 1),
          Scale(channels),
          nn.ReLU(inplace=True),
          nn.Conv2d(channels, channels, 3, 1, 1))
    elif mask == 'SCALE2':
      self.conv = nn.Sequential(
          nn.Conv2d(channels, channels, 3, 1, 1),
          Scale(channels),
          nn.ReLU(inplace=True),
          nn.Conv2d(channels, channels, 3, 1, 1),
          Scale(channels))
    elif mask == 'SCALE3':
      self.conv = nn.Sequential(
          nn.Conv2d(channels, channels, 3, 1, 1),
          nn.ReLU(inplace=True),
          nn.Conv2d(channels, channels, 3, 1, 1),
          Scale(channels))
    elif mask == 'BN':
      self.conv = nn.Sequential(
          nn.Conv2d(channels, channels, 3, 1, 1),
          nn.BatchNorm2d(channels),
          nn.ReLU(inplace=True),
          nn.Conv2d(channels, channels, 3, 1, 1))
    else:
      self.conv = nn.Sequential(
          nn.Conv2d(channels, channels, 3, 1, 1),
          nn.ReLU(inplace=True),
          nn.Conv2d(channels, channels, 3, 1, 1))

  def forward(self, x):
    fea = self.conv(x)
    return fea + x


class FENet(nn.Module):
  def __init__(self, channels=64):
    super(FENet, self).__init__()
    self.conv0 = nn.Conv2d(3, channels, 7, 1, 3)
    self.relu = nn.ReLU(inplace=True)
    blocks = []
    for _ in range(10):
      blocks.append(ResidualBlock(channels=channels, mask=None))
    self.block = nn.Sequential(*blocks)
    self.conv1 = nn.Conv2d(channels, 3, 7, 1, 3)

  def forward(self, x):
    f0 = self.conv0(x)
    fea = self.block(self.relu(f0))
    out = self.conv1(self.relu(f0 + fea))
    return out.tanh()


class OutBlock(nn.Module):
  def __init__(self, in_channels, conv_kernel_size, conv_stride, conv_pad,
               use_bias, lrelu_slope, output_scale, channels=64):
    super(OutBlock, self).__init__()
    self.conv2d_1 = nn.Conv2d(in_channels, channels, conv_kernel_size, conv_stride, padding=conv_pad, bias=use_bias)  # output channel num: channels # nopep8
    self.lrelu_1 = nn.LeakyReLU(lrelu_slope, inplace=True)
    self.conv2d_2 = nn.Conv2d(channels, 2, conv_kernel_size, conv_stride, padding=conv_pad, bias=use_bias)  # output channel num: 2 # nopep8
    self.tanh = nn.Tanh()
    self.output_scale = output_scale


class FENetWithBranch(nn.Module):
  def __init__(self, in_channels=1,
               channels=64,
               num_blocks=[4, 2, 2],
               mask=None,
               block_type='residual',
               out_channels=1,
               return_1x=False,
               **kwargs):
    super(FENetWithBranch, self).__init__()
    assert channels % 4 == 0
    assert block_type in ['residual', 'imdb']
    self.return_1x = return_1x

    if block_type.lower() == 'residual':
      block_fn = ResidualBlock
    elif block_type.lower() == 'imdb':
      block_fn = IMDBModule
    else:
      raise NotImplementedError

    self.stem = nn.Conv2d(in_channels, channels, 3, 1, 1)
    self.relu = nn.ReLU(inplace=True)

    blocks = []
    if num_blocks[0] > 0:
      for _ in range(num_blocks[0]):
        blocks.append(block_fn(channels=channels, mask=mask))
      self.block_base = nn.Sequential(*blocks)
    else:
      self.block_base = None

    blocks = []
    if num_blocks[1] > 0:
      for _ in range(num_blocks[1]):
        blocks.append(block_fn(channels=channels, mask=mask))
      self.block_1x = nn.Sequential(*blocks)
      self.out1 = nn.Conv2d(channels, out_channels, 3, 1, 1)
    else:
      self.block_1x = None

    blocks = []
    if num_blocks[2] > 0:
      for _ in range(num_blocks[2]):
        blocks.append(block_fn(channels=channels, mask=mask))
      self.block_2x = nn.Sequential(*blocks)
      self.block_2x_up = nn.PixelShuffle(2)
      self.out2 = nn.Conv2d(channels // 4, out_channels, 3, 1, 1)
    else:
      self.block_2x = None

  def forward(self, x):
    x = self.stem(x)

    if self.block_base is not None:
      base_x = self.block_base(self.relu(x))
    else:
      base_x = x

    if self.block_1x is not None:
      base_x = self.block_1x(self.relu(base_x))
      out_1x = self.out1(self.relu(x + base_x))

    if self.block_2x is not None:
      base_x = self.block_2x(self.relu(base_x))

    out_2x = self.relu(self.block_2x_up(x + base_x))
    out_2x = self.out2(out_2x)

    if self.return_1x:
      return out_1x, out_2x
    else:
      return out_2x.tanh()

#!<----------------------------------------------------------------------------
#!< FENet with Previous output
#!<----------------------------------------------------------------------------


class FENetWithWarp(nn.Module):

  def __init__(self, in_channels=1,
               out_channels=1,
               channels=64,
               num_blocks=[4, 2, 2],
               mask=None,
               block_type='residual',
               warp_scale=2,  # warp feature scale compared with input
               warp_channels=3):  # warp feature channels

    super(FENetWithWarp, self).__init__()

    self.in_channels = in_channels + warp_channels * warp_scale * warp_scale
    self.out_channels = out_channels
    self.scale = warp_scale
    assert self.scale in [1, 2, 4]

    self.backbone = FENetWithBranch(in_channels=self.in_channels,
                                    out_channels=out_channels,
                                    channels=channels,
                                    num_blocks=num_blocks,
                                    mask=mask,
                                    block_type=block_type)

    self.warp = nn.Sequential(
        nn.Conv2d(warp_channels * self.scale ** 2, warp_channels * self.scale ** 2, 1, 1, 0),
        nn.LeakyReLU(0.2, inplace=True))

    self.alignment = nn.Sequential(
        nn.Conv2d(self.in_channels, self.in_channels, 3, 1, 1),
        nn.LeakyReLU(0.2, inplace=True),
        nn.Conv2d(self.in_channels, self.in_channels, 1, 1, 0),
        nn.LeakyReLU(0.2, inplace=True))

  def forward(self, lr, feat):
    """inference with lr and feat

    Args:
        lr   ([torch.Tensor]): [n, c, h, w]
        feat ([torch.Tensor]): [n, c, h, w]

    Returns:
        hr [torch.Tensor]: [super resolution result.]
    """

    assert lr.ndim == 4 and feat.ndim == 4, f"{lr.ndim} vs {feat.ndim}"
    n, c, h, w = feat.shape
    s = self.scale

    feat = feat.reshape(n, c, s, h // s, s, w // s)
    feat = feat.permute(0, 1, 2, 4, 3, 5).reshape(n, c * s ** 2, h // s, w // s)

    x = torch.cat([self.warp(feat), lr], dim=1)
    x = self.alignment(x)
    x = self.backbone(x)

    return x

#!<----------------------------------------------------------------------------
#!< FENet with Gradient Guide
#!<----------------------------------------------------------------------------


class FENetWithGrad(nn.Module):
  def __init__(self, in_channels=1,
               channels=64,
               num_blocks=[4, 2, 2],
               grad_channels=16,
               grad_num_blocks=[4, 2, 2],
               mask=None,
               block_type='residual'):
    super(FENetWithGrad, self).__init__()
    assert channels % 4 == 0
    assert block_type in ['residual', 'imdb']

    self.grad_fn = tw.nn.GradientIntensity()

    # output channel
    if in_channels == 1:
      out_channels = 1
    else:
      out_channels = 3

    if block_type.lower() == 'residual':
      block_fn = ResidualBlock
    elif block_type.lower() == 'imdb':
      block_fn = IMDBModule

    # -----------------------------------------------------------------
    #  STEM BLOCK
    # -----------------------------------------------------------------
    self.stem = nn.Conv2d(in_channels, channels, 3, 1, 1)
    self.relu = nn.ReLU(inplace=True)

    blocks = [block_fn(channels=channels, mask=mask) for _ in range(num_blocks[0])]
    self.block_base = nn.Sequential(*blocks)

    blocks = [block_fn(channels=channels, mask=mask) for _ in range(num_blocks[1])]
    self.block_1x = nn.Sequential(*blocks)

    blocks = [block_fn(channels=channels, mask=mask) for _ in range(num_blocks[2])]
    self.block_2x = nn.Sequential(*blocks)

    # sr-upsample
    self.block_2x_up = nn.Sequential(nn.PixelShuffle(2), nn.Conv2d(channels // 4, channels // 4, 3, 1, 1))

    # sr-grad-fusion
    last_channel = (channels + grad_channels) // 4
    self.fusion = nn.Sequential(
        nn.Conv2d(last_channel, last_channel, 3, 1, 1),
        nn.ReLU(inplace=True),
        nn.Conv2d(last_channel, last_channel, 1, 1, 0))

    # sr-out
    self.out2 = nn.Conv2d(last_channel, out_channels, 3, 1, 1)

    # -----------------------------------------------------------------
    #  STEM BLOCK [GRADIENT]
    # -----------------------------------------------------------------
    self.stem_g = nn.Conv2d(in_channels, grad_channels, 3, 1, 1)
    self.relu_g = nn.ReLU(inplace=True)

    blocks = [block_fn(channels=grad_channels, mask=mask) for _ in range(grad_num_blocks[0])]
    self.block_base_g = nn.Sequential(
        nn.Conv2d(channels + grad_channels, grad_channels, 1, 1, 0),
        *blocks)

    blocks = [block_fn(channels=grad_channels, mask=mask) for _ in range(grad_num_blocks[1])]
    self.block_1x_g = nn.Sequential(
        nn.Conv2d(channels + grad_channels, grad_channels, 1, 1, 0),
        *blocks)

    blocks = [block_fn(channels=grad_channels, mask=mask) for _ in range(grad_num_blocks[2])]
    self.block_2x_g = nn.Sequential(
        nn.Conv2d(channels + grad_channels, grad_channels, 1, 1, 0),
        *blocks)

    last_g_channels = grad_channels // 4
    self.block_2x_up_g = nn.Sequential(nn.PixelShuffle(2), nn.Conv2d(last_g_channels, last_g_channels, 3, 1, 1))
    self.out2_g = nn.Conv2d(last_g_channels, out_channels, 1, 1, 0)

  def forward(self, x):

    g = self.grad_fn(x)

    stem_x = self.stem(x)
    stem_g = self.stem_g(g)

    x0 = self.block_base(self.relu(stem_x))
    x1 = self.block_1x(self.relu(x0))
    x2 = self.block_2x(self.relu(x1))
    x_2x = self.block_2x_up(x2 + stem_x)

    g0 = self.block_base_g(self.relu_g(torch.cat([x0, stem_g], dim=1)))
    g1 = self.block_1x_g(self.relu_g(torch.cat([x1, g0], dim=1)))
    g2 = self.block_2x_g(self.relu_g(torch.cat([x2, g1], dim=1)))
    g_2x = self.block_2x_up_g(g2 + stem_g)

    out_2x = self.fusion(torch.cat([x_2x, g_2x], dim=1))
    out_2x = self.out2(out_2x)
    out_2x = out_2x

    out_g_2x = self.out2_g(g_2x)

    return out_2x.tanh(), out_g_2x, g


#!<----------------------------------------------------------------------------
#!< FENet with MoCo method (self-supervised learning)
#!<----------------------------------------------------------------------------


class FENetEncoder(nn.Module):

  def __init__(self, in_channels=1, out_channels=32):
    super(FENetEncoder, self).__init__()

    self.E = nn.Sequential(
        nn.Conv2d(in_channels, 8, kernel_size=3, padding=1),
        nn.BatchNorm2d(8),
        nn.LeakyReLU(0.1, True),
        nn.Conv2d(8, 8, kernel_size=3, padding=1),
        nn.BatchNorm2d(8),
        nn.LeakyReLU(0.1, True),
        nn.Conv2d(8, 16, kernel_size=3, stride=2, padding=1),
        nn.BatchNorm2d(16),
        nn.LeakyReLU(0.1, True),
        nn.Conv2d(16, 16, kernel_size=3, padding=1),
        nn.BatchNorm2d(16),
        nn.LeakyReLU(0.1, True),
        nn.Conv2d(16, 32, kernel_size=3, stride=2, padding=1),
        nn.BatchNorm2d(32),
        nn.LeakyReLU(0.1, True),
        nn.Conv2d(32, out_channels, kernel_size=3, padding=1),
        nn.BatchNorm2d(out_channels),
        nn.LeakyReLU(0.1, True),
        # nn.AdaptiveAvgPool2d(1)
    )

    self.mlp = nn.Sequential(
        nn.Linear(out_channels, out_channels),
        nn.LeakyReLU(0.1, True),
        nn.Linear(out_channels, out_channels))

  def forward(self, x):

    feat = self.E(x).squeeze(-1).squeeze(-1)
    embedding = nn.functional.adaptive_avg_pool2d(feat, 1).squeeze()
    out = self.mlp(embedding)

    n, c, h, w = feat.shape

    feat = feat.reshape(n, c // 16, 4, 4, h, w)
    feat = feat.permute(0, 1, 2, 4, 3, 5).reshape(n, c // 16, h * 4, w * 4)
    return embedding, out, feat


class FENetWithMoco(nn.Module):

  def __init__(self, encoder, channels=32):
    super(FENetWithMoco, self).__init__()
    self.moco = tw.models.moco.MoCo(base_encoder=encoder,
                                    dim=channels,
                                    K=32 * channels,
                                    m=0.999,
                                    T=0.07)

  def forward(self, x_query, x_key):

    if self.training:
      # fea, logits, labels, feat
      return self.moco(x_query, x_key)

    else:
      return self.moco(x_query, None)


# if __name__ == "__main__":

  # # -------

  # net1 = FENetWithBranch(in_channels=3,
  #                        channels=32,
  #                        num_blocks=[4, 2, 2])
  # net1.eval()

  # tw.flops.register(net1)
  # with torch.no_grad():
  #   net1(torch.randn(1, 3, 640, 360))
  # print(tw.flops.accumulate(net1))
  # tw.flops.unregister(net1)

  # # -------

  # net2 = FENetWithGrad(in_channels=3,
  #                      channels=32,
  #                      num_blocks=[4, 2, 2],
  #                      grad_channels=8,
  #                      grad_num_blocks=[4, 2, 2])
  # net2.eval()

  # tw.flops.register(net2)
  # with torch.no_grad():
  #   net2(torch.randn(1, 3, 640, 360))
  # print(tw.flops.accumulate(net2))
  # tw.flops.unregister(net2)

  # net3 = FENetWithWarp(in_channels=1,
  #                      channels=32,
  #                      num_blocks=[4, 2, 2])
  # net3.eval()

  # with torch.no_grad():
  #   net3(torch.randn(1, 1, 360, 640), torch.randn(1, 1, 720, 1280))

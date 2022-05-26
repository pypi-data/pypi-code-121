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
"""Disentangled Representation Learning"""
import torch
from torch import nn
from torch.nn import functional as F
import tw


class FNet(nn.Module):
  def __init__(self, in_channels=6):
    super(FNet, self).__init__()
    self.conv_kernel_size = 3
    self.conv_stride = 1
    self.conv_use_bias = True
    self.lrelu_slope = 0.2
    self.pool_kernel_size = 2
    self.upsample_scale = 2.0
    self.max_velocity = 24.0
    self.conv_pad = self.conv_kernel_size // 2
    self.down_block_1 = DownBlock(in_channels, 32, self.conv_kernel_size, self.conv_stride, self.conv_pad, self.conv_use_bias, self.lrelu_slope, self.pool_kernel_size)  # nopep8
    self.down_block_2 = DownBlock(32, 64, self.conv_kernel_size, self.conv_stride, self.conv_pad, self.conv_use_bias, self.lrelu_slope, self.pool_kernel_size)  # nopep8
    self.down_block_3 = DownBlock(64, 128, self.conv_kernel_size, self.conv_stride, self.conv_pad, self.conv_use_bias, self.lrelu_slope, self.pool_kernel_size)  # nopep8
    self.up_block_1 = UpBlock(128, 256, self.conv_kernel_size, self.conv_stride, self.conv_pad, self.conv_use_bias, self.lrelu_slope, self.upsample_scale)  # nopep8
    self.up_block_2 = UpBlock(256, 128, self.conv_kernel_size, self.conv_stride, self.conv_pad, self.conv_use_bias, self.lrelu_slope, self.upsample_scale)  # nopep8
    self.up_block_3 = UpBlock(128, 64, self.conv_kernel_size, self.conv_stride, self.conv_pad, self.conv_use_bias, self.lrelu_slope, self.upsample_scale)  # nopep8
    self.out_block = OutBlock(64, self.conv_kernel_size, self.conv_stride, self.conv_pad, self.conv_use_bias, self.lrelu_slope, self.max_velocity)  # nopep8

  def forward(self, inputs):
    out = self.down_block_1(inputs)
    out = self.down_block_2(out)
    out = self.down_block_3(out)
    out = self.up_block_1(out)
    out = self.up_block_2(out)
    out = self.up_block_3(out)
    out = self.out_block(out)
    assert inputs.shape[2:] == out.shape[2:], (inputs.shape, out.shape)
    return out


# Down sample block in FNet
class DownBlock(nn.Module):
  def __init__(self, in_channels, out_channels, conv_kernel_size, conv_stride,
               conv_pad, use_bias, lrelu_slope, pooling_kernel_size):
    super(DownBlock, self).__init__()
    self.conv2d_1 = nn.Conv2d(in_channels, out_channels, conv_kernel_size, conv_stride, padding=conv_pad, bias=use_bias)  # nopep8
    self.lrelu_1 = nn.LeakyReLU(lrelu_slope, inplace=True)
    self.conv2d_2 = nn.Conv2d(out_channels, out_channels, conv_kernel_size, conv_stride, padding=conv_pad, bias=use_bias)  # nopep8
    self.lrelu_2 = nn.LeakyReLU(lrelu_slope, inplace=True)
    self.max_pool = nn.MaxPool2d(pooling_kernel_size)

  def forward(self, inputs):
    out = self.conv2d_1(inputs)
    out = self.lrelu_1(out)
    out = self.conv2d_2(out)
    out = self.lrelu_2(out)
    out = self.max_pool(out)
    return out


# Up sample block in FNet
class UpBlock(nn.Module):
  def __init__(self, in_channels, out_channels, conv_kernel_size,
               conv_stride, conv_pad, use_bias, lrelu_slope, upsample_scale):
    super(UpBlock, self).__init__()
    self.conv2d_1 = nn.Conv2d(in_channels, out_channels, conv_kernel_size, conv_stride, padding=conv_pad, bias=use_bias)  # nopep8
    self.lrelu_1 = nn.LeakyReLU(lrelu_slope, inplace=True)
    self.conv2d_2 = nn.Conv2d(out_channels, out_channels, conv_kernel_size, conv_stride, padding=conv_pad, bias=use_bias)  # nopep8
    self.lrelu_2 = nn.LeakyReLU(lrelu_slope, inplace=True)
    self.upsample_scale = upsample_scale

  def forward(self, inputs):
    out = self.conv2d_1(inputs)
    out = self.lrelu_1(out)
    out = self.conv2d_2(out)
    out = self.lrelu_2(out)
    out = nn.functional.interpolate(out, scale_factor=[self.upsample_scale, self.upsample_scale], mode='bilinear', align_corners=False)  # nopep8
    return out


class OutBlock(nn.Module):
  def __init__(self, in_channels, conv_kernel_size, conv_stride, conv_pad, use_bias, lrelu_slope, output_scale):
    super(OutBlock, self).__init__()
    self.conv2d_1 = nn.Conv2d(in_channels, 32, conv_kernel_size, conv_stride, padding=conv_pad, bias=use_bias)  # output channel num: 32 # nopep8
    self.lrelu_1 = nn.LeakyReLU(lrelu_slope, inplace=True)
    self.conv2d_2 = nn.Conv2d(32, 2, conv_kernel_size, conv_stride, padding=conv_pad, bias=use_bias)  # output channel num: 2 # nopep8
    self.tanh = nn.Tanh()
    self.output_scale = output_scale

  def forward(self, inputs):
    out = self.conv2d_1(inputs)
    out = self.lrelu_1(out)
    out = self.conv2d_2(out)
    out = self.tanh(out) * self.output_scale
    return out


#!------------------------------------------------------------------------
#!  Super resolution residual generator network G
#! Input     : current low-res frame x_t and warped last high-res frame w(g_{t-1}, v_t), where:
#!             - w(g_{t-1}, v_t) is represented with low-res spatial shape by SpaceToDepth operation
#!             - x_t and w(g_{t-1}, v_t) are concatenated in channel
#!             - g_{t-1} is last high-res frame generated by Generator
#!             - v_t is motion estimation between x_{t-1} and x_t, output of FNet
#! Output    : high resoultion residual for current frame
#! DataFormat: NCHW
#!------------------------------------------------------------------------

class GNet(nn.Module):
  def __init__(self, scale_factor, img_channels, resblock_num, resblock_channel, resblock_enable_bias=True):
    super(GNet, self).__init__()
    assert scale_factor in (1, 2, 4)  # only support 1, 2, 4 super resolution
    assert resblock_channel % (scale_factor ** 2) == 0, (resblock_channel, scale_factor)  # make sure pixel shuffle can work # nopep8
    self.scale_factor = scale_factor
    # hyper-parameters
    conv_kernel_size = 3
    conv_stride = 1
    conv_use_bias = True
    conv_padding = conv_kernel_size // 2
    # architecture
    # input stage
    # input LR + warped and pixel shuffled HR
    input_depth = img_channels * (scale_factor ** 2 + 1)
    self.conv2d_in = nn.Conv2d(input_depth, resblock_channel, conv_kernel_size, conv_stride, bias=conv_use_bias, padding=conv_padding)  # nopep8
    self.relu = nn.ReLU(inplace=True)
    # residual blocks stage
    self.res_blocks = nn.Sequential(*[ResidualBlock(resblock_channel, resblock_channel, conv_kernel_size, conv_stride, conv_padding, resblock_enable_bias) for _ in range(resblock_num)])  # nopep8
    # upsample with PixelShuffle
    self.pixel_shuffle = nn.PixelShuffle(self.scale_factor)
    pixel_shuffle_out_depth = resblock_channel // (scale_factor ** 2)
    # output stage
    self.conv2d_out = nn.Conv2d(pixel_shuffle_out_depth, img_channels, conv_kernel_size, conv_stride, bias=conv_use_bias, padding=conv_padding)  # nopep8

  def forward(self, inputs):
    # input stage
    out = inputs
    out = self.conv2d_in(out)
    out = self.relu(out)
    # residual blocks stage
    out = self.res_blocks(out)
    # upsample stage
    out = self.pixel_shuffle(out)
    # output stage
    out = self.conv2d_out(out)
    return out


class ResidualBlock(nn.Module):
  def __init__(self, in_channels, out_channels, conv_kernel_size, conv_stride, conv_padding, use_bias):
    super(ResidualBlock, self).__init__()
    self.conv_1 = nn.Conv2d(in_channels, out_channels, conv_kernel_size, conv_stride, bias=use_bias, padding=conv_padding)  # nopep8
    self.conv_2 = nn.Conv2d(out_channels, out_channels, conv_kernel_size, conv_stride, bias=use_bias, padding=conv_padding)  # nopep8
    self.relu = nn.ReLU(inplace=True)

  def forward(self, inputs):
    out = self.conv_1(inputs)
    out = self.relu(out)
    out = self.conv_2(out)
    out = out + inputs
    return out

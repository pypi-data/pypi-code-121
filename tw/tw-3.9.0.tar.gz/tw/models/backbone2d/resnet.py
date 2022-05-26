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
"""ResNets form torchvision.model """
import functools
import torch
from torch import functional
import torch.nn as nn
from tw.utils.checkpoint import load_state_dict_from_url

from tw.nn import FrozenBatchNorm2d
from tw.nn import AdaptiveAvgMaxPool2d
from tw.nn import AdaptiveCatAvgMaxPool2d
from tw.nn import SEModule
from tw.nn import EffectiveSEModule
from tw.nn import ECAModule
from tw.nn import CECAModule
from tw.nn import ChannelAttention
from tw.nn import SpatialAttention, CBAMModule

model_urls = {
    # pytorch official
    'resnet18': 'https://download.pytorch.org/models/resnet18-5c106cde.pth',
    'resnet34': 'https://download.pytorch.org/models/resnet34-333f7ec4.pth',
    'resnet50': 'https://download.pytorch.org/models/resnet50-19c8e357.pth',
    'resnet101': 'https://download.pytorch.org/models/resnet101-5d3b4d8f.pth',
    'resnet152': 'https://download.pytorch.org/models/resnet152-b121ed2d.pth',
    'resnext50_32x4d': 'https://download.pytorch.org/models/resnext50_32x4d-7cdf4587.pth',
    'resnext101_32x8d': 'https://download.pytorch.org/models/resnext101_32x8d-8ba56ff5.pth',
    'wide_resnet50_2': 'https://download.pytorch.org/models/wide_resnet50_2-95faca4d.pth',
    'wide_resnet101_2': 'https://download.pytorch.org/models/wide_resnet101_2-32ee1156.pth',

    # bag of tricks (mxnet impl)
    'resnet18d': 'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/resnet18d_ra2-48a79e06.pth',
    'resnet34d': 'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/resnet34d_ra2-f8dcfcaf.pth',
    'resnet26': 'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/resnet26-9aa10e23.pth',
    'resnet26d': 'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/resnet26d-69e92c46.pth',
    'resnet50d': 'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/resnet50d_ra2-464e36ba.pth',
    'resnet101d': 'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/resnet101d_ra2-2803ffab.pth',
    'resnet152d': 'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/resnet152d_ra2-5cac0439.pth',
    'resnet200d': 'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/resnet200d_ra2-bdba9bf9.pth',

    # resnext
    'resnext50d_32x4d': 'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/resnext50d_32x4d-103e99f8.pth',
    'resnext101_32x8d': 'https://download.pytorch.org/models/resnext101_32x8d-8ba56ff5.pth',
    'resnext50_32x4d': 'https://download.pytorch.org/models/resnext50_32x4d-7cdf4587.pth',

    #  ResNeXt models - Weakly Supervised Pretraining on Instagram Hashtags
    #  from https://github.com/facebookresearch/WSL-Images
    #  Please note the CC-BY-NC 4.0 license on theses weights, non-commercial use only.
    'ig_resnext101_32x8d': 'https://download.pytorch.org/models/ig_resnext101_32x8-c38310e5.pth',
    'ig_resnext101_32x16d': 'https://download.pytorch.org/models/ig_resnext101_32x16-c6f796b0.pth',
    'ig_resnext101_32x32d': 'https://download.pytorch.org/models/ig_resnext101_32x32-e4b90b00.pth',
    'ig_resnext101_32x48d': 'https://download.pytorch.org/models/ig_resnext101_32x48-3e41cc8a.pth',

    #  Semi-Supervised ResNe*t models from https://github.com/facebookresearch/semi-supervised-ImageNet1K-models
    #  Please note the CC-BY-NC 4.0 license on theses weights, non-commercial use only.
    'ssl_resnet18': 'https://dl.fbaipublicfiles.com/semiweaksupervision/model_files/semi_supervised_resnet18-d92f0530.pth',
    'ssl_resnet50': 'https://dl.fbaipublicfiles.com/semiweaksupervision/model_files/semi_supervised_resnet50-08389792.pth',
    'ssl_resnext50_32x4d': 'https://dl.fbaipublicfiles.com/semiweaksupervision/model_files/semi_supervised_resnext50_32x4-ddb3e555.pth',
    'ssl_resnext101_32x4d': 'https://dl.fbaipublicfiles.com/semiweaksupervision/model_files/semi_supervised_resnext101_32x4-dc43570a.pth',
    'ssl_resnext101_32x8d': 'https://dl.fbaipublicfiles.com/semiweaksupervision/model_files/semi_supervised_resnext101_32x8-2cfe2f8b.pth',
    'ssl_resnext101_32x16d': 'https://dl.fbaipublicfiles.com/semiweaksupervision/model_files/semi_supervised_resnext101_32x16-15fffa57.pth',

    #  Semi-Weakly Supervised ResNe*t models from https://github.com/facebookresearch/semi-supervised-ImageNet1K-models
    #  Please note the CC-BY-NC 4.0 license on theses weights, non-commercial use only.
    'swsl_resnet18': 'https://dl.fbaipublicfiles.com/semiweaksupervision/model_files/semi_weakly_supervised_resnet18-118f1556.pth',
    'swsl_resnet50': 'https://dl.fbaipublicfiles.com/semiweaksupervision/model_files/semi_weakly_supervised_resnet50-16a12f1b.pth',
    'swsl_resnext50_32x4d': 'https://dl.fbaipublicfiles.com/semiweaksupervision/model_files/semi_weakly_supervised_resnext50_32x4-72679e44.pth',
    'swsl_resnext101_32x4d': 'https://dl.fbaipublicfiles.com/semiweaksupervision/model_files/semi_weakly_supervised_resnext101_32x4-3f87e46b.pth',
    'swsl_resnext101_32x8d': 'https://dl.fbaipublicfiles.com/semiweaksupervision/model_files/semi_weakly_supervised_resnext101_32x8-b4712904.pth',
    'swsl_resnext101_32x16d': 'https://dl.fbaipublicfiles.com/semiweaksupervision/model_files/semi_weakly_supervised_resnext101_32x16-f3559a9c.pth',

    # Efficient Channel Attention ResNets
    'ecaresnet26t': 'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/ecaresnet26t_ra2-46609757.pth',
    'ecaresnetlight': 'https://imvl-automl-sh.oss-cn-shanghai.aliyuncs.com/darts/hyperml/hyperml/job_45402/outputs/ECAResNetLight_4f34b35b.pth',
    'ecaresnet50d': 'https://imvl-automl-sh.oss-cn-shanghai.aliyuncs.com/darts/hyperml/hyperml/job_45402/outputs/ECAResNet50D_833caf58.pth',
    'ecaresnet50d_pruned': 'https://imvl-automl-sh.oss-cn-shanghai.aliyuncs.com/darts/hyperml/hyperml/job_45899/outputs/ECAResNet50D_P_9c67f710.pth',
    'ecaresnet50t': 'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/ecaresnet50t_ra2-f7ac63c4.pth',
    'ecaresnet101d': 'https://imvl-automl-sh.oss-cn-shanghai.aliyuncs.com/darts/hyperml/hyperml/job_45402/outputs/ECAResNet101D_281c5844.pth',
    'ecaresnet101d_pruned': 'https://imvl-automl-sh.oss-cn-shanghai.aliyuncs.com/darts/hyperml/hyperml/job_45610/outputs/ECAResNet101D_P_75a3370e.pth',
    'ecaresnet269d': 'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/ecaresnet269d_320_ra2-7baa55cb.pth',

    # ResNets with anti-aliasing blur pool
    'resnetblur50': 'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-weights/resnetblur50-84f4748f.pth',

    # ResNet-RS models
    'resnetrs50': 'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-rs-weights/resnetrs50_ema-6b53758b.pth',
    'resnetrs101': 'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-rs-weights/resnetrs101_i192_ema-1509bbf6.pth',
    'resnetrs152': 'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-rs-weights/resnetrs152_i256_ema-a9aff7f9.pth',
    'resnetrs200': 'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-rs-weights/resnetrs200_ema-623d2f59.pth',
    'resnetrs270': 'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-rs-weights/resnetrs270_ema-b40e674c.pth',
    'resnetrs350': 'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-rs-weights/resnetrs350_i256_ema-5a1aa8f1.pth',
    'resnetrs420': 'https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-rs-weights/resnetrs420_ema-972dee69.pth',
}


def conv3x3(in_planes, out_planes, stride=1, groups=1, dilation=1):
  """3x3 convolution with padding"""
  return nn.Conv2d(in_planes,
                   out_planes,
                   kernel_size=3,
                   stride=stride,
                   padding=dilation,
                   groups=groups,
                   bias=False,
                   dilation=dilation)


def conv1x1(in_planes, out_planes, stride=1):
  """1x1 convolution"""
  return nn.Conv2d(in_planes,
                   out_planes,
                   kernel_size=1,
                   stride=stride,
                   bias=False)


class BasicBlock(nn.Module):
  expansion = 1
  __constants__ = ['downsample']

  def __init__(self, inplanes, planes, stride=1, downsample=None, groups=1,
               base_width=64, dilation=1, norm_layer=None):
    super(BasicBlock, self).__init__()
    if norm_layer is None:
      norm_layer = nn.BatchNorm2d
    if groups != 1 or base_width != 64:
      raise ValueError('BasicBlock only supports groups=1 and base_width=64')
    if dilation > 1:
      raise NotImplementedError("Dilation > 1 not supported in BasicBlock")
    # Both self.conv1 and self.downsample layers downsample the input when stride != 1
    self.conv1 = conv3x3(inplanes, planes, stride)
    self.bn1 = norm_layer(planes)
    self.relu = nn.ReLU(inplace=True)
    self.conv2 = conv3x3(planes, planes)
    self.bn2 = norm_layer(planes)
    self.downsample = downsample
    self.stride = stride

  def forward(self, x):
    identity = x

    out = self.conv1(x)
    out = self.bn1(out)
    out = self.relu(out)

    out = self.conv2(out)
    out = self.bn2(out)

    if self.downsample is not None:
      identity = self.downsample(x)

    out += identity
    out = self.relu(out)

    return out


class Bottleneck(nn.Module):
  expansion = 4
  __constants__ = ['downsample']

  def __init__(self, inplanes, planes, stride=1, downsample=None, groups=1,
               base_width=64, dilation=1, attention_layer=None, norm_layer=None):
    super(Bottleneck, self).__init__()
    if norm_layer is None:
      norm_layer = nn.BatchNorm2d
    width = int(planes * (base_width / 64.)) * groups
    # Both self.conv2 and self.downsample layers downsample the input when stride != 1
    self.conv1 = conv1x1(inplanes, width)
    self.bn1 = norm_layer(width)
    self.conv2 = conv3x3(width, width, stride, groups, dilation)
    self.bn2 = norm_layer(width)
    self.conv3 = conv1x1(width, planes * self.expansion)
    self.bn3 = norm_layer(planes * self.expansion)
    self.relu = nn.ReLU(inplace=True)
    self.downsample = downsample
    self.stride = stride

    if attention_layer is not None:
      self.se = attention_layer(planes * self.expansion)
    else:
      self.se = None

  def forward(self, x):
    identity = x

    out = self.conv1(x)
    out = self.bn1(out)
    out = self.relu(out)

    out = self.conv2(out)
    out = self.bn2(out)
    out = self.relu(out)

    out = self.conv3(out)
    out = self.bn3(out)

    if self.downsample is not None:
      identity = self.downsample(x)

    if self.se is not None:
      out = self.se(out)

    out += identity
    out = self.relu(out)

    return out


class ResNet(nn.Module):

  """ResNet and ResNeXt

    This ResNet impl supports a number of stem and downsample options based on the v1c, v1d, v1e, and v1s
    variants included in the MXNet Gluon ResNetV1b model. The C and D variants are also discussed in the
    'Bag of Tricks' paper: https://arxiv.org/pdf/1812.01187. The B variant is equivalent to torchvision default.

    ResNet variants (the same modifications can be used in SE/ResNeXt models as well):
      * normal, b - 7x7 stem, stem_width = 64, same as torchvision ResNet, NVIDIA ResNet 'v1.5', Gluon v1b
      * c - 3 layer deep 3x3 stem, stem_width = 32 (32, 32, 64)
      * d - 3 layer deep 3x3 stem, stem_width = 32 (32, 32, 64), average pool in downsample
      * e - 3 layer deep 3x3 stem, stem_width = 64 (64, 64, 128), average pool in downsample
      * s - 3 layer deep 3x3 stem, stem_width = 64 (64, 64, 128)
      * t - 3 layer deep 3x3 stem, stem width = 32 (24, 48, 64), average pool in downsample
      * tn - 3 layer deep 3x3 stem, stem width = 32 (24, 32, 64), average pool in downsample

    ResNeXt
      * normal - 7x7 stem, stem_width = 64, standard cardinality and base widths
      * same c,d, e, s variants as ResNet can be enabled

  Args:
      block ([nn.Module]): block type
        - Bottleneck
        - BasicBlock
      layers ([int]): number of layers in each block (e.g. [3, 4, 6, 3])
      num_classes (int): number of classification classes. Defaults to 1000.
      cardinality (int): number of convolution groups for 3x3 conv in Bottleneck.
      base_width (int): factor determining bottleneck channels. `planes * base_width / 64 * cardinality`
      in_channels (int): number of input (color) channels. Defaults to 3.
      stem_width (int): number of channels in stem convolutions.
      stem_type (str):
        - None: default - a single 7x7 conv with a width of stem_width
        - 'deep' - three 3x3 convolution layers of widths stem_width, stem_width, stem_width * 2
        - 'tiered' - three 3x3 conv layers of widths stem_width//4 * 3, stem_width, stem_width * 2
      stem_pool_layer (nn.Module): default to None.
      avg_down (bool): whether to use average pooling (or max pool) for projection skip connection between stages/downsample.
      global_pool (str)
        - default: 'avg'
        - max
        - avgmax
        - catavgmax
      norm_layer (nn.Module): default to nn.BatchNorm2d
      act_layer (nn.Module): default to nn.ReLU
      output_stride (int): default to 32.
      zero_init_residual (bool, optional): [description]. Defaults to False.
      output_backbone (bool, optional): [description]. Defaults to False.

  Raises:
      ValueError: [description]
  """

  MEAN = [0.485, 0.456, 0.406]
  STD = [0.229, 0.224, 0.225]
  SIZE = [224, 224]
  SCALE = 255
  CROP = 0.875

  def __init__(self, block=Bottleneck, layers=[3, 4, 6, 3], zero_init_residual=False,
               in_channels=3, stem_type=None, stem_width=64, stem_pool_layer=None,   # stem layer related
               norm_layer=None, act_layer=None,  # layer type
               base_width=64, cardinality=1, output_stride=32, avg_down=False,  # inter-blocks
               global_pool='avg', num_classes=1000,  # head
               output_backbone=False):
    super(ResNet, self).__init__()

    # average downsample ref:
    self._avg_down = avg_down

    # output stride
    assert output_stride in [8, 16, 32]

    # wheather output low-level backbone (C2, C3, C4, C5)
    self.output_backbone = output_backbone

    # decide normalize layer
    if norm_layer is None:
      norm_layer = nn.BatchNorm2d
    self._norm_layer = norm_layer

    # decide norm layer
    if act_layer is None:
      act_layer = nn.ReLU
    self._act_layer = act_layer

    #!< build stem layer
    if stem_type is None:
      self.inplanes = 64
      self.conv1 = nn.Conv2d(in_channels, self.inplanes, kernel_size=7, stride=2, padding=3, bias=False)
    elif stem_type == 'tiered':
      self.inplanes = stem_width * 2
      ch0, ch1 = 3 * stem_width // 4, stem_width
      self.conv1 = nn.Sequential(
          nn.Conv2d(in_channels, ch0, 3, 2, 1, bias=False),
          norm_layer(ch0),
          act_layer(inplace=True),
          nn.Conv2d(ch0, ch1, 3, 1, 1, bias=False),
          norm_layer(ch1),
          act_layer(inplace=True),
          nn.Conv2d(ch1, self.inplanes, 3, 1, 1, bias=False))
    elif stem_type == 'deep':
      self.inplanes = stem_width * 2
      ch0, ch1 = stem_width, stem_width
      self.conv1 = nn.Sequential(
          nn.Conv2d(in_channels, ch0, 3, 2, 1, bias=False),
          norm_layer(ch0),
          act_layer(inplace=True),
          nn.Conv2d(ch0, ch1, 3, 1, 1, bias=False),
          norm_layer(ch1),
          act_layer(inplace=True),
          nn.Conv2d(ch1, self.inplanes, 3, 1, 1, bias=False))
    else:
      raise NotImplementedError(stem_type)
    self.bn1 = norm_layer(self.inplanes)
    self.relu = act_layer(inplace=True)

    #!< stem pool
    if stem_pool_layer is None:
      self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
    elif stem_pool_layer == 'rs':
      self.maxpool = nn.Sequential(
          nn.Conv2d(self.inplanes, self.inplanes, 3, stride=2, padding=1, bias=False),
          norm_layer(self.inplanes),
          act_layer(inplace=True))
    else:
      raise NotImplementedError(stem_pool_layer)

    #!< build blocks
    stage_modules = self._make_blocks(
        block=block,
        channels=[64, 128, 256, 512],
        num_blocks=layers,
        inplanes=self.inplanes,
        output_stride=output_stride,
        cardinality=cardinality,
        base_width=base_width)
    for stage in stage_modules:
      self.add_module(*stage)

    #!< build classifier head
    inplanes = 512 * block.expansion
    # build pool head
    if global_pool == 'avg':
      self.global_pool = nn.AdaptiveAvgPool2d((1, 1))
    elif global_pool == 'max':
      self.global_pool = nn.AdaptiveMaxPool2d((1, 1))
    elif global_pool == 'avgmax':
      self.global_pool = AdaptiveAvgMaxPool2d(1)
    elif global_pool == 'catavgam':
      self.global_pool = AdaptiveCatAvgMaxPool2d(1)
      inplanes *= 2
    else:
      raise NotImplementedError(global_pool)

    # build fc
    if num_classes <= 0:
      self.fc = nn.Identity()
    else:
      self.fc = nn.Linear(inplanes, num_classes)

    for m in self.modules():
      if isinstance(m, nn.Conv2d):
        nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
      elif isinstance(m, (nn.BatchNorm2d, nn.GroupNorm)):
        nn.init.constant_(m.weight, 1)
        nn.init.constant_(m.bias, 0)

    # Zero-initialize the last BN in each residual branch,
    # so that the residual branch starts with zeros, and each residual block behaves like an identity.
    # This improves the model by 0.2~0.3% according to https://arxiv.org/abs/1706.02677
    if zero_init_residual:
      for m in self.modules():
        if isinstance(m, Bottleneck):
          nn.init.constant_(m.bn3.weight, 0)
        elif isinstance(m, BasicBlock):
          nn.init.constant_(m.bn2.weight, 0)

  def _make_blocks(self, block: Bottleneck,
                   channels=[64, 128, 256, 512],
                   num_blocks=[3, 4, 6, 3],
                   inplanes=64,
                   output_stride=32,
                   cardinality=1,
                   base_width=64,
                   **kwargs):
    """make resnet blocks consists of a series of convs.
    """
    stages = []
    net_stride = 4
    dilation = 1
    prev_dilation = 1
    for i, (planes, num_block) in enumerate(zip(channels, num_blocks)):
      name = f'layer{i + 1}'

      # build stride
      stride = 1 if i == 0 else 2
      if net_stride >= output_stride:
        dilation *= stride
        stride = 1
      else:
        net_stride *= stride

      # downsample if necessary
      if stride != 1 or inplanes != planes * block.expansion:
        if self._avg_down:
          if dilation == 1:
            avg_stride = stride
          else:
            avg_stride = 1
          if stride == 1 and dilation == 1:
            pool = nn.Identity()
          else:
            if avg_stride == 1 and dilation > 1:
              avg_pool_fn = AvgPool2dSame
            else:
              avg_pool_fn = nn.AvgPool2d
            pool = avg_pool_fn(2, avg_stride, ceil_mode=True, count_include_pad=False)
          downsample = nn.Sequential(
              pool,
              nn.Conv2d(inplanes, planes * block.expansion, 1, stride=1, padding=0, bias=False),
              self._norm_layer(planes * block.expansion))
        else:
          downsample = nn.Sequential(
              conv1x1(inplanes, planes * block.expansion, stride),
              self._norm_layer(planes * block.expansion))
      else:
        downsample = None

      # build successive blocks
      blocks = []
      for block_idx in range(num_block):
        # only downsample for first layer
        if block_idx != 0:
          downsample = None
          stride = 1
        # add block
        blocks.append(block(
            inplanes,
            planes,
            stride,
            downsample,
            groups=cardinality,
            base_width=base_width,
            dilation=dilation,
            norm_layer=self._norm_layer))
        # update channels
        prev_dilation = dilation
        inplanes = planes * block.expansion

      # add-in
      stages.append((name, nn.Sequential(*blocks)))

    return stages

  def forward(self, x):
    x = self.conv1(x)
    x = self.bn1(x)
    x = self.relu(x)
    x = self.maxpool(x)

    c2 = self.layer1(x)
    c3 = self.layer2(c2)
    c4 = self.layer3(c3)
    c5 = self.layer4(c4)

    if self.output_backbone:
      return c2, c3, c4, c5

    x = self.global_pool(c5)
    x = torch.flatten(x, 1)
    x = self.fc(x)

    return x


def _resnet(arch, block, layers, pretrained, **kwargs):
  model = ResNet(block, layers, **kwargs)
  if pretrained:
    load_state_dict_from_url(model, model_urls[arch])
  return model


def resnet18(pretrained=False, **kwargs):
  r"""ResNet-18 model from
  `"Deep Residual Learning for Image Recognition" <https://arxiv.org/pdf/1512.03385.pdf>`_

  Args:
      pretrained (bool): If True, returns a model pre-trained on ImageNet
      progress (bool): If True, displays a progress bar of the download to stderr
  """
  return _resnet('resnet18', BasicBlock, [2, 2, 2, 2], pretrained, **kwargs)


def resnet34(pretrained=False, **kwargs):
  r"""ResNet-34 model from
  `"Deep Residual Learning for Image Recognition" <https://arxiv.org/pdf/1512.03385.pdf>`_

  Args:
      pretrained (bool): If True, returns a model pre-trained on ImageNet
      progress (bool): If True, displays a progress bar of the download to stderr
  """
  return _resnet('resnet34', BasicBlock, [3, 4, 6, 3], pretrained, **kwargs)


def resnet50(pretrained=False, **kwargs):
  r"""ResNet-50 model from
  `"Deep Residual Learning for Image Recognition" <https://arxiv.org/pdf/1512.03385.pdf>`_

  Args:
      pretrained (bool): If True, returns a model pre-trained on ImageNet
      progress (bool): If True, displays a progress bar of the download to stderr
  """
  return _resnet('resnet50', Bottleneck, [3, 4, 6, 3], pretrained, **kwargs)


def resnet101(pretrained=False, **kwargs):
  r"""ResNet-101 model from
  `"Deep Residual Learning for Image Recognition" <https://arxiv.org/pdf/1512.03385.pdf>`_

  Args:
      pretrained (bool): If True, returns a model pre-trained on ImageNet
      progress (bool): If True, displays a progress bar of the download to stderr
  """
  return _resnet('resnet101', Bottleneck, [3, 4, 23, 3], pretrained, **kwargs)


def resnet152(pretrained=False, **kwargs):
  r"""ResNet-152 model from
  `"Deep Residual Learning for Image Recognition" <https://arxiv.org/pdf/1512.03385.pdf>`_

  Args:
      pretrained (bool): If True, returns a model pre-trained on ImageNet
      progress (bool): If True, displays a progress bar of the download to stderr
  """
  return _resnet('resnet152', Bottleneck, [3, 8, 36, 3], pretrained, **kwargs)


def resnext50_32x4d(pretrained=False, **kwargs):
  r"""ResNeXt-50 32x4d model from
  `"Aggregated Residual Transformation for Deep Neural Networks" <https://arxiv.org/pdf/1611.05431.pdf>`_

  Args:
      pretrained (bool): If True, returns a model pre-trained on ImageNet
      progress (bool): If True, displays a progress bar of the download to stderr
  """
  kwargs['groups'] = 32
  kwargs['width_per_group'] = 4
  return _resnet('resnext50_32x4d', Bottleneck, [3, 4, 6, 3], pretrained, **kwargs)


def resnext101_32x8d(pretrained=False, **kwargs):
  r"""ResNeXt-101 32x8d model from
  `"Aggregated Residual Transformation for Deep Neural Networks" <https://arxiv.org/pdf/1611.05431.pdf>`_

  Args:
      pretrained (bool): If True, returns a model pre-trained on ImageNet
      progress (bool): If True, displays a progress bar of the download to stderr
  """
  kwargs['groups'] = 32
  kwargs['width_per_group'] = 8
  return _resnet('resnext101_32x8d', Bottleneck, [3, 4, 23, 3], pretrained, **kwargs)


def wide_resnet50_2(pretrained=False, **kwargs):
  r"""Wide ResNet-50-2 model from
  `"Wide Residual Networks" <https://arxiv.org/pdf/1605.07146.pdf>`_

  The model is the same as ResNet except for the bottleneck number of channels
  which is twice larger in every block. The number of channels in outer 1x1
  convolutions is the same, e.g. last block in ResNet-50 has 2048-512-2048
  channels, and in Wide ResNet-50-2 has 2048-1024-2048.

  Args:
      pretrained (bool): If True, returns a model pre-trained on ImageNet
      progress (bool): If True, displays a progress bar of the download to stderr
  """
  kwargs['width_per_group'] = 64 * 2
  return _resnet('wide_resnet50_2', Bottleneck, [3, 4, 6, 3], pretrained, **kwargs)


def wide_resnet101_2(pretrained=False, **kwargs):
  r"""Wide ResNet-101-2 model from
  `"Wide Residual Networks" <https://arxiv.org/pdf/1605.07146.pdf>`_

  The model is the same as ResNet except for the bottleneck number of channels
  which is twice larger in every block. The number of channels in outer 1x1
  convolutions is the same, e.g. last block in ResNet-50 has 2048-512-2048
  channels, and in Wide ResNet-50-2 has 2048-1024-2048.

  Args:
      pretrained (bool): If True, returns a model pre-trained on ImageNet
      progress (bool): If True, displays a progress bar of the download to stderr
  """
  kwargs['width_per_group'] = 64 * 2
  return _resnet('wide_resnet101_2', Bottleneck, [3, 4, 23, 3], pretrained, **kwargs)


def resnet18d(pretrained=False, **kwargs):
  """Constructs a ResNet-18-D model.
  """
  model_args = dict(stem_width=32, stem_type='deep', avg_down=True, **kwargs)
  return _resnet('resnet18d', BasicBlock, [2, 2, 2, 2], pretrained, **model_args)


def resnet34d(pretrained=False, **kwargs):
  """Constructs a ResNet-34-D model.
  """
  model_args = dict(stem_width=32, stem_type='deep', avg_down=True, **kwargs)
  return _resnet('resnet34d', BasicBlock, [3, 4, 6, 3], pretrained, **model_args)


def resnet26(pretrained=False, **kwargs):
  """Constructs a ResNet-26-D model.
  """
  return _resnet('resnet26', Bottleneck, [2, 2, 2, 2], pretrained, **kwargs)


def resnet26d(pretrained=False, **kwargs):
  """Constructs a ResNet-26-D model.
  """
  model_args = dict(stem_width=32, stem_type='deep', avg_down=True, **kwargs)
  return _resnet('resnet26d', Bottleneck, [2, 2, 2, 2], pretrained, **model_args)


def resnet50d(pretrained=False, **kwargs):
  """Constructs a ResNet-50-D model.
  """
  model_args = dict(stem_width=32, stem_type='deep', avg_down=True, **kwargs)
  return _resnet('resnet50d', Bottleneck, [3, 4, 6, 3], pretrained, **model_args)


def resnet101d(pretrained=False, **kwargs):
  """Constructs a ResNet-101-D model.
  """
  model_args = dict(stem_width=32, stem_type='deep', avg_down=True, **kwargs)
  return _resnet('resnet101d', Bottleneck, [3, 4, 23, 3], pretrained, **model_args)


def resnet152d(pretrained=False, **kwargs):
  """Constructs a ResNet-152-D model.
  """
  model_args = dict(stem_width=32, stem_type='deep', avg_down=True, **kwargs)
  return _resnet('resnet152d', Bottleneck, [3, 8, 36, 3], pretrained, **model_args)


def resnet200d(pretrained=False, **kwargs):
  """Constructs a ResNet-200-D model.
  """
  model_args = dict(stem_width=32, stem_type='deep', avg_down=True, **kwargs)
  return _resnet('resnet200d', Bottleneck, [3, 24, 36, 3], pretrained, **model_args)


def resnext50d_32x4d(pretrained=False, **kwargs):
  """Constructs a ResNeXt50d-32x4d model. ResNext50 w/ deep stem & avg pool downsample
  """
  model_args = dict(cardinality=32, base_width=4, stem_width=32, stem_type='deep', avg_down=True, **kwargs)
  return _resnet('resnext50d_32x4d', Bottleneck, [3, 4, 6, 3], pretrained, **model_args)


def resnext101_32x4d(pretrained=False, **kwargs):
  """Constructs a ResNeXt-101 32x4d model.
  """
  model_args = dict(cardinality=32, base_width=4, **kwargs)
  return _resnet('resnext101_32x4d', Bottleneck, [3, 4, 23, 3], pretrained, **model_args)


def resnext101_64x4d(pretrained=False, **kwargs):
  """Constructs a ResNeXt101-64x4d model.
  """
  model_args = dict(cardinality=64, base_width=4, **kwargs)
  return _resnet('resnext101_64x4d', Bottleneck, [3, 4, 23, 3], pretrained, **model_args)


def ig_resnext101_32x8d(pretrained=True, **kwargs):
  """Constructs a ResNeXt-101 32x8 model pre-trained on weakly-supervised data
  and finetuned on ImageNet from Figure 5 in
  `"Exploring the Limits of Weakly Supervised Pretraining" <https://arxiv.org/abs/1805.00932>`_
  Weights from https://pytorch.org/hub/facebookresearch_WSL-Images_resnext/
  """
  model_args = dict(cardinality=32, base_width=8, **kwargs)
  return _resnet('ig_resnext101_32x8d', Bottleneck, [3, 4, 23, 3], pretrained, **model_args)


def ig_resnext101_32x16d(pretrained=True, **kwargs):
  """Constructs a ResNeXt-101 32x16 model pre-trained on weakly-supervised data
  and finetuned on ImageNet from Figure 5 in
  `"Exploring the Limits of Weakly Supervised Pretraining" <https://arxiv.org/abs/1805.00932>`_
  Weights from https://pytorch.org/hub/facebookresearch_WSL-Images_resnext/
  """
  model_args = dict(cardinality=32, base_width=16, **kwargs)
  return _resnet('ig_resnext101_32x16d', Bottleneck, [3, 4, 23, 3], pretrained, **model_args)


def ig_resnext101_32x32d(pretrained=True, **kwargs):
  """Constructs a ResNeXt-101 32x32 model pre-trained on weakly-supervised data
  and finetuned on ImageNet from Figure 5 in
  `"Exploring the Limits of Weakly Supervised Pretraining" <https://arxiv.org/abs/1805.00932>`_
  Weights from https://pytorch.org/hub/facebookresearch_WSL-Images_resnext/
  """
  model_args = dict(cardinality=32, base_width=32, **kwargs)
  return _resnet('ig_resnext101_32x32d', Bottleneck, [3, 4, 23, 3], pretrained, **model_args)


def ig_resnext101_32x48d(pretrained=True, **kwargs):
  """Constructs a ResNeXt-101 32x48 model pre-trained on weakly-supervised data
  and finetuned on ImageNet from Figure 5 in
  `"Exploring the Limits of Weakly Supervised Pretraining" <https://arxiv.org/abs/1805.00932>`_
  Weights from https://pytorch.org/hub/facebookresearch_WSL-Images_resnext/
  """
  model_args = dict(cardinality=32, base_width=48, **kwargs)
  return _resnet('ig_resnext101_32x48d', Bottleneck, [3, 4, 23, 3], pretrained, **model_args)


def ssl_resnet18(pretrained=True, **kwargs):
  """Constructs a semi-supervised ResNet-18 model pre-trained on YFCC100M dataset and finetuned on ImageNet
  `"Billion-scale Semi-Supervised Learning for Image Classification" <https://arxiv.org/abs/1905.00546>`_
  Weights from https://github.com/facebookresearch/semi-supervised-ImageNet1K-models/
  """
  return _resnet('ssl_resnet18', BasicBlock, [2, 2, 2, 2], pretrained, **kwargs)


def ssl_resnet50(pretrained=True, **kwargs):
  """Constructs a semi-supervised ResNet-50 model pre-trained on YFCC100M dataset and finetuned on ImageNet
  `"Billion-scale Semi-Supervised Learning for Image Classification" <https://arxiv.org/abs/1905.00546>`_
  Weights from https://github.com/facebookresearch/semi-supervised-ImageNet1K-models/
  """
  return _resnet('ssl_resnet50', Bottleneck, [3, 4, 6, 3], pretrained, **kwargs)


def ssl_resnext50_32x4d(pretrained=True, **kwargs):
  """Constructs a semi-supervised ResNeXt-50 32x4 model pre-trained on YFCC100M dataset and finetuned on ImageNet
  `"Billion-scale Semi-Supervised Learning for Image Classification" <https://arxiv.org/abs/1905.00546>`_
  Weights from https://github.com/facebookresearch/semi-supervised-ImageNet1K-models/
  """
  model_args = dict(cardinality=32, base_width=4, **kwargs)
  return _resnet('ssl_resnext50_32x4d', Bottleneck, [3, 4, 6, 3], pretrained, **model_args)


def ssl_resnext101_32x4d(pretrained=True, **kwargs):
  """Constructs a semi-supervised ResNeXt-101 32x4 model pre-trained on YFCC100M dataset and finetuned on ImageNet
  `"Billion-scale Semi-Supervised Learning for Image Classification" <https://arxiv.org/abs/1905.00546>`_
  Weights from https://github.com/facebookresearch/semi-supervised-ImageNet1K-models/
  """
  model_args = dict(cardinality=32, base_width=4, **kwargs)
  return _resnet('ssl_resnext101_32x4d', Bottleneck, [3, 4, 23, 3], pretrained, **model_args)


def ssl_resnext101_32x8d(pretrained=True, **kwargs):
  """Constructs a semi-supervised ResNeXt-101 32x8 model pre-trained on YFCC100M dataset and finetuned on ImageNet
  `"Billion-scale Semi-Supervised Learning for Image Classification" <https://arxiv.org/abs/1905.00546>`_
  Weights from https://github.com/facebookresearch/semi-supervised-ImageNet1K-models/
  """
  model_args = dict(cardinality=32, base_width=8, **kwargs)
  return _resnet('ssl_resnext101_32x8d', Bottleneck, [3, 4, 23, 3], pretrained, **model_args)


def ssl_resnext101_32x16d(pretrained=True, **kwargs):
  """Constructs a semi-supervised ResNeXt-101 32x16 model pre-trained on YFCC100M dataset and finetuned on ImageNet
  `"Billion-scale Semi-Supervised Learning for Image Classification" <https://arxiv.org/abs/1905.00546>`_
  Weights from https://github.com/facebookresearch/semi-supervised-ImageNet1K-models/
  """
  model_args = dict(cardinality=32, base_width=16, **kwargs)
  return _resnet('ssl_resnext101_32x16d', Bottleneck, [3, 4, 23, 3], pretrained, **model_args)


def swsl_resnet18(pretrained=True, **kwargs):
  """Constructs a semi-weakly supervised Resnet-18 model pre-trained on 1B weakly supervised
     image dataset and finetuned on ImageNet.
     `"Billion-scale Semi-Supervised Learning for Image Classification" <https://arxiv.org/abs/1905.00546>`_
     Weights from https://github.com/facebookresearch/semi-supervised-ImageNet1K-models/
  """
  return _resnet('swsl_resnet18', BasicBlock, [2, 2, 2, 2], pretrained, **kwargs)


def swsl_resnet50(pretrained=True, **kwargs):
  """Constructs a semi-weakly supervised ResNet-50 model pre-trained on 1B weakly supervised
     image dataset and finetuned on ImageNet.
     `"Billion-scale Semi-Supervised Learning for Image Classification" <https://arxiv.org/abs/1905.00546>`_
     Weights from https://github.com/facebookresearch/semi-supervised-ImageNet1K-models/
  """
  return _resnet('swsl_resnet50', Bottleneck, [3, 4, 6, 3], pretrained, **kwargs)


def swsl_resnext50_32x4d(pretrained=True, **kwargs):
  """Constructs a semi-weakly supervised ResNeXt-50 32x4 model pre-trained on 1B weakly supervised
     image dataset and finetuned on ImageNet.
     `"Billion-scale Semi-Supervised Learning for Image Classification" <https://arxiv.org/abs/1905.00546>`_
     Weights from https://github.com/facebookresearch/semi-supervised-ImageNet1K-models/
  """
  model_args = dict(cardinality=32, base_width=4, **kwargs)
  return _resnet('swsl_resnext50_32x4d', Bottleneck, [3, 4, 6, 3], pretrained, **model_args)


def swsl_resnext101_32x4d(pretrained=True, **kwargs):
  """Constructs a semi-weakly supervised ResNeXt-101 32x4 model pre-trained on 1B weakly supervised
     image dataset and finetuned on ImageNet.
     `"Billion-scale Semi-Supervised Learning for Image Classification" <https://arxiv.org/abs/1905.00546>`_
     Weights from https://github.com/facebookresearch/semi-supervised-ImageNet1K-models/
  """
  model_args = dict(cardinality=32, base_width=4, **kwargs)
  return _resnet('swsl_resnext101_32x4d', Bottleneck, [3, 4, 23, 3], pretrained, **model_args)


def swsl_resnext101_32x8d(pretrained=True, **kwargs):
  """Constructs a semi-weakly supervised ResNeXt-101 32x8 model pre-trained on 1B weakly supervised
     image dataset and finetuned on ImageNet.
     `"Billion-scale Semi-Supervised Learning for Image Classification" <https://arxiv.org/abs/1905.00546>`_
     Weights from https://github.com/facebookresearch/semi-supervised-ImageNet1K-models/
  """
  model_args = dict(cardinality=32, base_width=8, **kwargs)
  return _resnet('swsl_resnext101_32x8d', Bottleneck, [3, 4, 23, 3], pretrained, **model_args)


def swsl_resnext101_32x16d(pretrained=True, **kwargs):
  """Constructs a semi-weakly supervised ResNeXt-101 32x16 model pre-trained on 1B weakly supervised
     image dataset and finetuned on ImageNet.
     `"Billion-scale Semi-Supervised Learning for Image Classification" <https://arxiv.org/abs/1905.00546>`_
     Weights from https://github.com/facebookresearch/semi-supervised-ImageNet1K-models/
  """
  model_args = dict(cardinality=32, base_width=16, **kwargs)
  return _resnet('swsl_resnext101_32x16d', Bottleneck, [3, 4, 23, 3], pretrained, **model_args)


def resnetrs50(pretrained=False, **kwargs):
  """Constructs a ResNet-RS-50 model.
  Paper: Revisiting ResNets - https://arxiv.org/abs/2103.07579
  Pretrained weights from https://github.com/tensorflow/tpu/tree/bee9c4f6/models/official/resnet/resnet_rs
  """
  attention = functools.partial(SEModule, rd_ratio=0.25)
  block = functools.partial(Bottleneck, attention_layer=attention)
  block.expansion = Bottleneck.expansion
  model_args = dict(stem_width=32, stem_type='deep', stem_pool_layer='rs', avg_down=True, **kwargs)
  model = _resnet('resnetrs50', block, [3, 4, 6, 3], pretrained, **model_args)
  model.SIZE = [160, 160]
  model.CROP = 0.91
  return model


def resnetrs101(pretrained=False, **kwargs):
  """Constructs a ResNet-RS-101 model.
  Paper: Revisiting ResNets - https://arxiv.org/abs/2103.07579
  Pretrained weights from https://github.com/tensorflow/tpu/tree/bee9c4f6/models/official/resnet/resnet_rs
  """
  attention = functools.partial(SEModule, rd_ratio=0.25)
  block = functools.partial(Bottleneck, attention_layer=attention)
  block.expansion = Bottleneck.expansion
  model_args = dict(stem_width=32, stem_type='deep', stem_pool_layer='rs', avg_down=True, **kwargs)
  model = _resnet('resnetrs101', Bottleneck, [3, 4, 23, 3], pretrained, **model_args)
  model.SIZE = [192, 192]
  model.CROP = 0.94
  return model


def resnetrs152(pretrained=False, **kwargs):
  """Constructs a ResNet-RS-152 model.
  Paper: Revisiting ResNets - https://arxiv.org/abs/2103.07579
  Pretrained weights from https://github.com/tensorflow/tpu/tree/bee9c4f6/models/official/resnet/resnet_rs
  """
  attention = functools.partial(SEModule, rd_ratio=0.25)
  block = functools.partial(Bottleneck, attention_layer=attention)
  block.expansion = Bottleneck.expansion
  model_args = dict(stem_width=32, stem_type='deep', stem_pool_layer='rs', avg_down=True, **kwargs)
  model = _resnet('resnetrs152', Bottleneck, [3, 8, 36, 3], pretrained, **model_args)
  model.SIZE = [256, 256]
  model.CROP = 1.0
  return model


def resnetrs200(pretrained=False, **kwargs):
  """Constructs a ResNet-RS-200 model.
  Paper: Revisiting ResNets - https://arxiv.org/abs/2103.07579
  Pretrained weights from https://github.com/tensorflow/tpu/tree/bee9c4f6/models/official/resnet/resnet_rs
  """
  attention = functools.partial(SEModule, rd_ratio=0.25)
  block = functools.partial(Bottleneck, attention_layer=attention)
  block.expansion = Bottleneck.expansion
  model_args = dict(stem_width=32, stem_type='deep', stem_pool_layer='rs', avg_down=True, **kwargs)
  model = _resnet('resnetrs200', Bottleneck, [3, 24, 36, 3], pretrained, **model_args)
  model.SIZE = [256, 256]
  model.CROP = 1.0
  return model


def resnetrs270(pretrained=False, **kwargs):
  """Constructs a ResNet-RS-270 model.
  Paper: Revisiting ResNets - https://arxiv.org/abs/2103.07579
  Pretrained weights from https://github.com/tensorflow/tpu/tree/bee9c4f6/models/official/resnet/resnet_rs
  """
  attention = functools.partial(SEModule, rd_ratio=0.25)
  block = functools.partial(Bottleneck, attention_layer=attention)
  block.expansion = Bottleneck.expansion
  model_args = dict(stem_width=32, stem_type='deep', stem_pool_layer='rs', avg_down=True, **kwargs)
  model = _resnet('resnetrs270', Bottleneck, [4, 29, 53, 4], pretrained, **model_args)
  model.SIZE = [256, 256]
  model.CROP = 1.0
  return model


def resnetrs350(pretrained=False, **kwargs):
  """Constructs a ResNet-RS-350 model.
  Paper: Revisiting ResNets - https://arxiv.org/abs/2103.07579
  Pretrained weights from https://github.com/tensorflow/tpu/tree/bee9c4f6/models/official/resnet/resnet_rs
  """
  attention = functools.partial(SEModule, rd_ratio=0.25)
  block = functools.partial(Bottleneck, attention_layer=attention)
  block.expansion = Bottleneck.expansion
  model_args = dict(stem_width=32, stem_type='deep', stem_pool_layer='rs', avg_down=True, **kwargs)
  model = _resnet('resnetrs350', Bottleneck, [4, 36, 72, 4], pretrained, **model_args)
  model.SIZE = [288, 288]
  model.CROP = 1.0
  return model


def resnetrs420(pretrained=False, **kwargs):
  """Constructs a ResNet-RS-420 model
  Paper: Revisiting ResNets - https://arxiv.org/abs/2103.07579
  Pretrained weights from https://github.com/tensorflow/tpu/tree/bee9c4f6/models/official/resnet/resnet_rs
  """
  attention = functools.partial(SEModule, rd_ratio=0.25)
  block = functools.partial(Bottleneck, attention_layer=attention)
  block.expansion = Bottleneck.expansion
  model_args = dict(stem_width=32, stem_type='deep', stem_pool_layer='rs', avg_down=True, **kwargs)
  model = _resnet('resnetrs420', Bottleneck, [4, 44, 87, 4], pretrained, **model_args)
  model.SIZE = [320, 320]
  model.CROP = 1.0
  return model


def ecaresnet26t(pretrained=False, **kwargs):
  """Constructs an ECA-ResNeXt-26-T model.
  This is technically a 28 layer ResNet, like a 'D' bag-of-tricks model but with tiered 24, 32, 64 channels
  in the deep stem and ECA attn.
  """
  block = functools.partial(Bottleneck, attention_layer=ECAModule)
  block.expansion = Bottleneck.expansion
  model_args = dict(stem_width=32, stem_type='tiered', avg_down=True, **kwargs)
  model = _resnet('ecaresnet26t', block, [2, 2, 2, 2], pretrained, **model_args)
  model.SIZE = [256, 256]
  model.CROP = 0.95
  return model


def ecaresnet50d(pretrained=False, **kwargs):
  """Constructs a ResNet-50-D model with eca.
  """
  block = functools.partial(Bottleneck, attention_layer=ECAModule)
  block.expansion = Bottleneck.expansion
  model_args = dict(stem_width=32, stem_type='deep', avg_down=True, **kwargs)
  return _resnet('ecaresnet50d', block, [3, 4, 6, 3], pretrained, **model_args)


def ecaresnet50d_pruned(pretrained=False, **kwargs):
  """Constructs a ResNet-50-D model pruned with eca.
      The pruning has been obtained using https://arxiv.org/pdf/2002.08258.pdf
  """
  block = functools.partial(Bottleneck, attention_layer=ECAModule)
  block.expansion = Bottleneck.expansion
  model_args = dict(stem_width=32, stem_type='deep', avg_down=True, **kwargs)
  return _resnet('ecaresnet50d_pruned', block, [3, 4, 6, 3], pretrained, pruned=True, **model_args)


def ecaresnet50t(pretrained=False, **kwargs):
  """Constructs an ECA-ResNet-50-T model.
  Like a 'D' bag-of-tricks model but with tiered 24, 32, 64 channels in the deep stem and ECA attn.
  """
  block = functools.partial(Bottleneck, attention_layer=ECAModule)
  block.expansion = Bottleneck.expansion
  model_args = dict(stem_width=32, stem_type='tiered', avg_down=True, **kwargs)
  model = _resnet('ecaresnet50t', block, [3, 4, 6, 3], pretrained, **model_args)
  model.SIZE = [256, 256]
  model.CROP = 0.95
  return model


def ecaresnetlight(pretrained=False, **kwargs):
  """Constructs a ResNet-50-D light model with eca.
  """
  block = functools.partial(Bottleneck, attention_layer=ECAModule)
  block.expansion = Bottleneck.expansion
  model_args = dict(stem_width=32, avg_down=True, **kwargs)
  return _resnet('ecaresnetlight', block, [1, 1, 11, 3], pretrained, **model_args)


def ecaresnet101d(pretrained=False, **kwargs):
  """Constructs a ResNet-101-D model with eca.
  """
  block = functools.partial(Bottleneck, attention_layer=ECAModule)
  block.expansion = Bottleneck.expansion
  model_args = dict(stem_width=32, stem_type='deep', avg_down=True, **kwargs)
  return _resnet('ecaresnet101d', block, [3, 4, 23, 3], pretrained, **model_args)


def ecaresnet101d_pruned(pretrained=False, **kwargs):
  """Constructs a ResNet-101-D model pruned with eca.
     The pruning has been obtained using https://arxiv.org/pdf/2002.08258.pdf
  """
  block = functools.partial(Bottleneck, attention_layer=ECAModule)
  block.expansion = Bottleneck.expansion
  model_args = dict(stem_width=32, stem_type='deep', avg_down=True, **kwargs)
  return _resnet('ecaresnet101d_pruned', block, [3, 4, 23, 3], pretrained, pruned=True, **model_args)


def ecaresnet200d(pretrained=False, **kwargs):
  """Constructs a ResNet-200-D model with ECA.
  """
  block = functools.partial(Bottleneck, attention_layer=ECAModule)
  block.expansion = Bottleneck.expansion
  model_args = dict(stem_width=32, stem_type='deep', avg_down=True, **kwargs)
  model = _resnet('ecaresnet200d', block, [3, 24, 36, 3], pretrained, **model_args)
  model.SIZE = [256, 256]
  model.CROP = 0.94
  return model


def ecaresnet269d(pretrained=False, **kwargs):
  """Constructs a ResNet-269-D model with ECA.
  """
  block = functools.partial(Bottleneck, attention_layer=ECAModule)
  block.expansion = Bottleneck.expansion
  model_args = dict(stem_width=32, stem_type='deep', avg_down=True, **kwargs)
  model = _resnet('ecaresnet269d', block, [3, 30, 48, 8], pretrained, **model_args)
  model.SIZE = [320, 320]
  model.CROP = 0.95
  return model


def ecaresnext26t_32x4d(pretrained=False, **kwargs):
  """Constructs an ECA-ResNeXt-26-T model.
  This is technically a 28 layer ResNet, like a 'D' bag-of-tricks model but with tiered 24, 32, 64 channels
  in the deep stem. This model replaces SE module with the ECA module
  """
  block = functools.partial(Bottleneck, attention_layer=ECAModule)
  block.expansion = Bottleneck.expansion
  model_args = dict(cardinality=32, base_width=4, stem_width=32, stem_type='tiered', avg_down=True, **kwargs)
  return _resnet('ecaresnext26t_32x4d', block, [2, 2, 2, 2], pretrained, **model_args)


def ecaresnext50t_32x4d(pretrained=False, **kwargs):
  """Constructs an ECA-ResNeXt-50-T model.
  This is technically a 28 layer ResNet, like a 'D' bag-of-tricks model but with tiered 24, 32, 64 channels
  in the deep stem. This model replaces SE module with the ECA module
  """
  block = functools.partial(Bottleneck, attention_layer=ECAModule)
  block.expansion = Bottleneck.expansion
  model_args = dict(cardinality=32, base_width=4, stem_width=32, stem_type='tiered', avg_down=True, **kwargs)
  return _resnet('ecaresnext50t_32x4d', block, [2, 2, 2, 2], pretrained, **model_args)

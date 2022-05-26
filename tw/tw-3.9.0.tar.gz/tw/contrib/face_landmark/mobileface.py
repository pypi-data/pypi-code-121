# Copyright 2021 The KaiJIN Authors. All Rights Reserved.
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
"""Reference
  https://github.com/cunjian/pytorch_face_landmark

  Implemented:

    'MobileNet_GDConv',
    'MobileNet_GDConv_56',
    'MobileNet_GDConv_SE',
    'MobileFaceNet',
    'PFLD',

"""
import os
import math

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.nn.init as init
import torchvision.models as models

import cv2
import numpy as np
import tw


#!<--------------------------------------------------------------------------
#!< MobileNet_GDConv
#!<--------------------------------------------------------------------------


class ConvBlock(nn.Module):
  def __init__(self, inp, oup, k, s, p, dw=False, linear=False):
    super(ConvBlock, self).__init__()
    self.linear = linear
    if dw:
      self.conv = nn.Conv2d(inp, oup, k, s, p, groups=inp, bias=False)
    else:
      self.conv = nn.Conv2d(inp, oup, k, s, p, bias=False)
    self.bn = nn.BatchNorm2d(oup)
    if not linear:
      self.prelu = nn.PReLU(oup)

  def forward(self, x):
    x = self.conv(x)
    x = self.bn(x)
    if self.linear:
      return x
    else:
      return self.prelu(x)


# SE module
# https://github.com/wujiyang/Face_Pytorch/blob/master/backbone/cbam.py
class SEModule(nn.Module):
  '''Squeeze and Excitation Module'''

  def __init__(self, channels, reduction):
    super(SEModule, self).__init__()
    self.avg_pool = nn.AdaptiveAvgPool2d(1)
    self.fc1 = nn.Conv2d(channels, channels // reduction, kernel_size=1, padding=0, bias=False)
    self.relu = nn.ReLU(inplace=True)
    self.fc2 = nn.Conv2d(channels // reduction, channels, kernel_size=1, padding=0, bias=False)
    self.sigmoid = nn.Sigmoid()

  def forward(self, x):
    input = x
    x = self.avg_pool(x)
    x = self.fc1(x)
    x = self.relu(x)
    x = self.fc2(x)
    x = self.sigmoid(x)

    return input * x

# USE global depthwise convolution layer. Compatible with MobileNetV2 (224×224), MobileNetV2_ExternalData (224×224)


class MobileNet_GDConv(nn.Module):
  def __init__(self, num_classes):
    super(MobileNet_GDConv, self).__init__()
    self.pretrain_net = models.mobilenet_v2(pretrained=False)
    self.base_net = nn.Sequential(*list(self.pretrain_net.children())[:-1])
    self.linear7 = ConvBlock(1280, 1280, (7, 7), 1, 0, dw=True, linear=True)
    self.linear1 = ConvBlock(1280, num_classes, 1, 1, 0, linear=True)

  def forward(self, x):
    x = self.base_net(x)
    x = self.linear7(x)
    x = self.linear1(x)
    x = x.view(x.size(0), -1)
    return x


#!<--------------------------------------------------------------------------
#!< MobileNet_GDConv_56
#!<--------------------------------------------------------------------------


# USE global depthwise convolution layer. Compatible with MobileNetV2 (56×56)
class MobileNet_GDConv_56(nn.Module):
  def __init__(self, num_classes):
    super(MobileNet_GDConv_56, self).__init__()
    self.pretrain_net = models.mobilenet_v2(pretrained=False)
    self.base_net = nn.Sequential(*list(self.pretrain_net.children())[:-1])
    self.linear7 = ConvBlock(1280, 1280, (2, 2), 1, 0, dw=True, linear=True)
    self.linear1 = ConvBlock(1280, num_classes, 1, 1, 0, linear=True)

  def forward(self, x):
    x = self.base_net(x)
    x = self.linear7(x)
    x = self.linear1(x)
    x = x.view(x.size(0), -1)
    return x


#!<--------------------------------------------------------------------------
#!< MobileNet_GDConv_SE
#!<--------------------------------------------------------------------------

# MobileNetV2 with SE; Compatible with MobileNetV2_SE (224×224) and MobileNetV2_SE_RE (224×224)
class MobileNet_GDConv_SE(nn.Module):
  def __init__(self, num_classes):
    super(MobileNet_GDConv_SE, self).__init__()
    self.pretrain_net = models.mobilenet_v2(pretrained=True)
    self.base_net = nn.Sequential(*list(self.pretrain_net.children())[:-1])
    self.linear7 = ConvBlock(1280, 1280, (7, 7), 1, 0, dw=True, linear=True)
    self.linear1 = ConvBlock(1280, num_classes, 1, 1, 0, linear=True)
    self.attention = SEModule(1280, 8)

  def forward(self, x):
    x = self.base_net(x)
    x = self.attention(x)
    x = self.linear7(x)
    x = self.linear1(x)
    x = x.view(x.size(0), -1)
    return x

#!<--------------------------------------------------------------------------
#!< MobileFaceNet
#!<--------------------------------------------------------------------------


##################################  Original Arcface Model ##################

class Flatten(nn.Module):
  def forward(self, input):
    return input.view(input.size(0), -1)

##################################  MobileFaceNet ###########################


class Conv_block(nn.Module):
  def __init__(self, in_c, out_c, kernel=(1, 1), stride=(1, 1), padding=(0, 0), groups=1):
    super(Conv_block, self).__init__()
    self.conv = nn.Conv2d(in_c, out_channels=out_c, kernel_size=kernel,
                          groups=groups, stride=stride, padding=padding, bias=False)
    self.bn = nn.BatchNorm2d(out_c)
    self.prelu = nn.PReLU(out_c)

  def forward(self, x):
    x = self.conv(x)
    x = self.bn(x)
    x = self.prelu(x)
    return x


class Linear_block(nn.Module):
  def __init__(self, in_c, out_c, kernel=(1, 1), stride=(1, 1), padding=(0, 0), groups=1):
    super(Linear_block, self).__init__()
    self.conv = nn.Conv2d(in_c, out_channels=out_c, kernel_size=kernel,
                          groups=groups, stride=stride, padding=padding, bias=False)
    self.bn = nn.BatchNorm2d(out_c)

  def forward(self, x):
    x = self.conv(x)
    x = self.bn(x)
    return x


class Depth_Wise(nn.Module):
  def __init__(self, in_c, out_c, residual=False, kernel=(3, 3), stride=(2, 2), padding=(1, 1), groups=1):
    super(Depth_Wise, self).__init__()
    self.conv = Conv_block(in_c, out_c=groups, kernel=(1, 1), padding=(0, 0), stride=(1, 1))
    self.conv_dw = Conv_block(groups, groups, groups=groups, kernel=kernel, padding=padding, stride=stride)
    self.project = Linear_block(groups, out_c, kernel=(1, 1), padding=(0, 0), stride=(1, 1))
    self.residual = residual

  def forward(self, x):
    if self.residual:
      short_cut = x
    x = self.conv(x)
    x = self.conv_dw(x)
    x = self.project(x)
    if self.residual:
      output = short_cut + x
    else:
      output = x
    return output


class Residual(nn.Module):
  def __init__(self, c, num_block, groups, kernel=(3, 3), stride=(1, 1), padding=(1, 1)):
    super(Residual, self).__init__()
    modules = []
    for _ in range(num_block):
      modules.append(Depth_Wise(c, c, residual=True, kernel=kernel, padding=padding, stride=stride, groups=groups))
    self.model = nn.Sequential(*modules)

  def forward(self, x):
    return self.model(x)


class GNAP(nn.Module):
  def __init__(self, embedding_size):
    super(GNAP, self).__init__()
    assert embedding_size == 512
    self.bn1 = nn.BatchNorm2d(512, affine=False)
    self.pool = nn.AdaptiveAvgPool2d((1, 1))

    self.bn2 = nn.BatchNorm1d(512, affine=False)

  def forward(self, x):
    x = self.bn1(x)
    x_norm = torch.norm(x, 2, 1, True)
    x_norm_mean = torch.mean(x_norm)
    weight = x_norm_mean / x_norm
    x = x * weight
    x = self.pool(x)
    x = x.view(x.shape[0], -1)
    feature = self.bn2(x)
    return feature


class GDC(nn.Module):
  def __init__(self, embedding_size):
    super(GDC, self).__init__()
    self.conv_6_dw = Linear_block(512, 512, groups=512, kernel=(7, 7), stride=(1, 1), padding=(0, 0))
    self.conv_6_flatten = nn.Flatten()
    self.linear = nn.Linear(512, embedding_size, bias=False)
    #self.bn = BatchNorm1d(embedding_size, affine=False)
    self.bn = nn.BatchNorm1d(embedding_size)

  def forward(self, x):
    x = self.conv_6_dw(x)
    x = self.conv_6_flatten(x)
    x = self.linear(x)
    x = self.bn(x)
    return x


class MobileFaceNet(nn.Module):
  def __init__(self, input_size, embedding_size=512, output_name="GDC"):
    super(MobileFaceNet, self).__init__()
    assert output_name in ["GNAP", 'GDC']
    assert input_size[0] in [112]
    self.conv1 = Conv_block(3, 64, kernel=(3, 3), stride=(2, 2), padding=(1, 1))
    self.conv2_dw = Conv_block(64, 64, kernel=(3, 3), stride=(1, 1), padding=(1, 1), groups=64)
    self.conv_23 = Depth_Wise(64, 64, kernel=(3, 3), stride=(2, 2), padding=(1, 1), groups=128)
    self.conv_3 = Residual(64, num_block=4, groups=128, kernel=(3, 3), stride=(1, 1), padding=(1, 1))
    self.conv_34 = Depth_Wise(64, 128, kernel=(3, 3), stride=(2, 2), padding=(1, 1), groups=256)
    self.conv_4 = Residual(128, num_block=6, groups=256, kernel=(3, 3), stride=(1, 1), padding=(1, 1))
    self.conv_45 = Depth_Wise(128, 128, kernel=(3, 3), stride=(2, 2), padding=(1, 1), groups=512)
    self.conv_5 = Residual(128, num_block=2, groups=256, kernel=(3, 3), stride=(1, 1), padding=(1, 1))
    self.conv_6_sep = Conv_block(128, 512, kernel=(1, 1), stride=(1, 1), padding=(0, 0))
    if output_name == "GNAP":
      self.output_layer = GNAP(512)
    else:
      self.output_layer = GDC(embedding_size)

    self._initialize_weights()

  def _initialize_weights(self):
    for m in self.modules():
      if isinstance(m, nn.Conv2d):
        nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
        if m.bias is not None:
          m.bias.data.zero_()
      elif isinstance(m, nn.BatchNorm2d):
        m.weight.data.fill_(1)
        m.bias.data.zero_()
      elif isinstance(m, nn.Linear):
        nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
        if m.bias is not None:
          m.bias.data.zero_()

  def forward(self, x):
    out = self.conv1(x)
    out = self.conv2_dw(out)
    out = self.conv_23(out)
    out = self.conv_3(out)
    out = self.conv_34(out)
    out = self.conv_4(out)
    out = self.conv_45(out)
    out = self.conv_5(out)

    conv_features = self.conv_6_sep(out)
    out = self.output_layer(conv_features)
    return out, conv_features


#!<--------------------------------------------------------------------------
#!< PFLDInference
#!<--------------------------------------------------------------------------


def conv_bn(inp, oup, kernel, stride, padding=1):
  return nn.Sequential(
      nn.Conv2d(inp, oup, kernel, stride, padding, bias=False),
      nn.BatchNorm2d(oup),
      nn.ReLU(inplace=True))


def conv_1x1_bn(inp, oup):
  return nn.Sequential(
      nn.Conv2d(inp, oup, 1, 1, 0, bias=False),
      nn.BatchNorm2d(oup),
      nn.ReLU(inplace=True))


class InvertedResidual(nn.Module):
  def __init__(self, inp, oup, stride, use_res_connect, expand_ratio=6):
    super(InvertedResidual, self).__init__()
    self.stride = stride
    assert stride in [1, 2]

    self.use_res_connect = use_res_connect

    self.conv = nn.Sequential(
        nn.Conv2d(inp, inp * expand_ratio, 1, 1, 0, bias=False),
        nn.BatchNorm2d(inp * expand_ratio),
        nn.ReLU(inplace=True),
        nn.Conv2d(
            inp * expand_ratio,
            inp * expand_ratio,
            3,
            stride,
            1,
            groups=inp * expand_ratio,
            bias=False),
        nn.BatchNorm2d(inp * expand_ratio),
        nn.ReLU(inplace=True),
        nn.Conv2d(inp * expand_ratio, oup, 1, 1, 0, bias=False),
        nn.BatchNorm2d(oup),
    )

  def forward(self, x):
    if self.use_res_connect:
      return x + self.conv(x)
    else:
      return self.conv(x)


class PFLDInference(nn.Module):

  def __init__(self):
    super(PFLDInference, self).__init__()

    self.conv1 = nn.Conv2d(
        3, 64, kernel_size=3, stride=2, padding=1, bias=False)
    self.bn1 = nn.BatchNorm2d(64)
    self.relu = nn.ReLU(inplace=True)
    '''
        self.conv2 = nn.Conv2d(
            64, 64, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        '''
    # use Depth-wise pooling
    self.dw_pool = nn.Conv2d(64, 64, 3, stride=1, padding=1, groups=64, bias=False)
    self.dw_bn = nn.BatchNorm2d(64)
    self.conv1_extra = nn.Conv2d(64, 64, 1, stride=1, padding=0, bias=False)
    self.relu = nn.ReLU(inplace=True)

    self.conv3_1 = InvertedResidual(64, 64, 2, False, 1)

    self.block3_2 = InvertedResidual(64, 64, 1, True, 1)
    self.block3_3 = InvertedResidual(64, 64, 1, True, 1)
    self.block3_4 = InvertedResidual(64, 64, 1, True, 1)
    self.block3_5 = InvertedResidual(64, 64, 1, True, 1)

    self.conv4_1 = InvertedResidual(64, 128, 2, False, 1)

    self.conv5_1 = InvertedResidual(128, 128, 1, False, 2)
    self.block5_2 = InvertedResidual(128, 128, 1, True, 2)
    self.block5_3 = InvertedResidual(128, 128, 1, True, 2)
    self.block5_4 = InvertedResidual(128, 128, 1, True, 2)
    self.block5_5 = InvertedResidual(128, 128, 1, True, 2)
    self.block5_6 = InvertedResidual(128, 128, 1, True, 2)

    self.conv6_1 = InvertedResidual(128, 16, 1, False, 1)  # [16, 14, 14]

    self.conv7 = conv_bn(16, 32, 3, 2)  # [32, 7, 7]
    self.conv8 = nn.Conv2d(32, 128, 7, 1, 0)  # [128, 1, 1]
    self.bn8 = nn.BatchNorm2d(128)

    self.avg_pool1 = nn.AvgPool2d(14)
    self.avg_pool2 = nn.AvgPool2d(7)
    self.fc = nn.Linear(176, 136)
    '''
        self.fc_aux = nn.Linear(176, 3)

        self.conv1_aux = conv_bn(64, 128, 3, 2)
        self.conv2_aux = conv_bn(128, 128, 3, 1)
        self.conv3_aux = conv_bn(128, 32, 3, 2)
        self.conv4_aux = conv_bn(32, 128, 7, 1)
        self.max_pool1_aux = nn.MaxPool2d(3)
        self.fc1_aux = nn.Linear(128, 32)
        self.fc2_aux = nn.Linear(32 + 176, 3)
        '''

  def forward(self, x):  # x: 3, 112, 112
    x = self.relu(self.bn1(self.conv1(x)))  # [64, 56, 56]
    # x = self.relu(self.bn2(self.conv2(x)))  # [64, 56, 56]
    x = self.relu(self.conv1_extra(self.dw_bn(self.dw_pool(x))))
    x = self.conv3_1(x)
    x = self.block3_2(x)
    x = self.block3_3(x)
    x = self.block3_4(x)
    out1 = self.block3_5(x)

    x = self.conv4_1(out1)
    x = self.conv5_1(x)
    x = self.block5_2(x)
    x = self.block5_3(x)
    x = self.block5_4(x)
    x = self.block5_5(x)
    x = self.block5_6(x)
    x = self.conv6_1(x)
    x1 = self.avg_pool1(x)
    x1 = x1.view(x1.size(0), -1)

    x = self.conv7(x)
    x2 = self.avg_pool2(x)
    x2 = x2.view(x2.size(0), -1)

    x3 = self.relu(self.conv8(x))
    x3 = x3.view(x1.size(0), -1)

    multi_scale = torch.cat([x1, x2, x3], 1)
    landmarks = self.fc(multi_scale)

    '''
        aux = self.conv1_aux(out1)
        aux = self.conv2_aux(aux)
        aux = self.conv3_aux(aux)
        aux = self.conv4_aux(aux)
        aux = self.max_pool1_aux(aux)
        aux = aux.view(aux.size(0), -1)
        aux = self.fc1_aux(aux)
        aux = torch.cat([aux, multi_scale], 1)
        pose = self.fc2_aux(aux)

        return pose, landmarks
        '''
    return landmarks

#!<--------------------------------------------------------------------------
#!< Wrapper
#!<--------------------------------------------------------------------------


class MobileFace():

  def __init__(self, net='MobileFaceNet', device='cpu', pretrain=None):

    assert os.path.exists(pretrain)
    assert net in [
        'MobileNet_GDConv',
        'MobileNet_GDConv_56',
        'MobileNet_GDConv_SE',
        'MobileFaceNet',
        'PFLD',
    ]

    if net == 'MobileNet_GDConv':
      self.model = MobileNet_GDConv(136)

    elif net == 'MobileNet_GDConv_56':
      self.model = MobileNet_GDConv_56(136)

    elif net == 'MobileNet_GDConv_SE':
      self.model = MobileNet_GDConv_SE(136)

    elif net == 'MobileFaceNet':
      self.model = MobileFaceNet([112, 112], 136)

    elif net == 'PFLD':
      self.model = PFLDInference()

    else:
      raise NotImplementedError(net)

    self.net = net

    content = torch.load(pretrain, map_location='cpu')['state_dict']
    content = tw.checkpoint.replace_prefix(content, 'module.', '')
    self.model.load_state_dict(content)
    self.model = self.model.to(device).eval()
    self.device = device

    # vgg mean and std
    self.mean = np.asarray([0.485, 0.456, 0.406])
    self.std = np.asarray([0.229, 0.224, 0.225])

  def preprocess(self, image):
    """np.numpy format [0, 255] uint8 RGB H, W, C

    Args:
        image (np.array): [description]

    Returns:
        [type]: [description]
    """

    # rgb to bgr
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if self.net in ['MobileNet_GDConv', 'MobileNet_GDConv_SE']:
      img = cv2.resize(image, (224, 224))
      img = ((img / 255.0) - self.mean) / self.std
      img = torch.from_numpy(img).to(self.device)
      img = img.float().permute(2, 0, 1).unsqueeze(0)
    elif self.net in ['MobileNet_GDConv_56']:
      img = cv2.resize(image, (56, 56))
      img = ((img / 255.0) - self.mean) / self.std
      img = torch.from_numpy(img).to(self.device)
      img = img.float().permute(2, 0, 1).unsqueeze(0)
    else:
      img = cv2.resize(image, (112, 112))
      img = torch.from_numpy(img).to(self.device)
      img = img.float().div(255).permute(2, 0, 1).unsqueeze(0)

    return img

  def postprocess(self, landmarks, x, y, w, h):
    """reproject to original pic.

    Args:
        landmarks ([type]): [description]
        x ([type]): left
        y ([type]): top
        w ([type]): image width
        h ([type]): image height

    Returns:
        [type]: [description]
    """

    assert len(landmarks.shape) == 2
    landmarks[:, 0] = landmarks[:, 0] * w + x
    landmarks[:, 1] = landmarks[:, 1] * h + y

    return landmarks

  def detect(self, faces):
    """Facial image is [0, 1] BGR [N, C, H, W] tensor

    Args:
        faces ([type]): [N, C, H, W], it should be processed by preprocess to
          resize to specific size.

    Returns:
        [type]: [N, 2] (x, y)
    """

    assert len(faces.shape) == 4 and isinstance(faces, torch.Tensor)
    if self.net == 'MobileFaceNet':
      return self.model(faces)[0].reshape(-1, 2)
    else:
      return self.model(faces).reshape(-1, 2)

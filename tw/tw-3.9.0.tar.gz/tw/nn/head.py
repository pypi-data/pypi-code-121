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
"""Network Header:

   BoundingBox Head:
    RoIBoxHeadSSD:
    RoIBoxHeadYOLO:
    RoIBoxHeadFCOS:
    RoIBoxHeadRetinaNet:

"""
import math
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
import tw

from tw.nn.conv import ConvModule

#!<----------------------------------------------------------------------------
#!< SSD Head
#!<----------------------------------------------------------------------------


class RoIBoxHeadSSD(nn.Module):
  """Single-Shot Detector Head with default 6 branch to output. Every branch
    outputs cls and reg tensor.
  """

  def __init__(self, arch='ssd',
               num_classes=81,
               in_channels=(512, 1024, 512, 256, 256, 256),
               anchor_ratios=([2], [2, 3], [2, 3], [2, 3], [2], [2])):
    """Convert feature maps to reg branch and cls branch"""
    super(RoIBoxHeadSSD, self).__init__()
    assert len(anchor_ratios) == len(in_channels)
    # add into
    reg_convs, cls_convs = [], []
    self.num_classes = num_classes
    # add default ratio with 1
    self.num_anchors = [len(ratios) * 2 + 2 for ratios in anchor_ratios]

    # generate bbox head
    for i, chs in enumerate(in_channels):
      reg_conv = []
      cls_conv = []

      if arch == 'ssdlite':
        reg_conv += [nn.Conv2d(chs, chs, 3, 1, 1, groups=chs, bias=False),
                     nn.BatchNorm2d(chs),
                     nn.ReLU(inplace=True)]
        cls_conv += [nn.Conv2d(chs, chs, 3, 1, 1, groups=chs, bias=False),
                     nn.BatchNorm2d(chs),
                     nn.ReLU(inplace=True)]
        reg_conv += [nn.Conv2d(chs, 4 * self.num_anchors[i], 1, 1, 0)]
        cls_conv += [nn.Conv2d(chs, num_classes * self.num_anchors[i], 1, 1, 0)]

      if arch == 'mssd':
        reg_conv += [nn.Conv2d(chs, 4 * self.num_anchors[i], 1, 1, 0)]
        cls_conv += [nn.Conv2d(chs, num_classes * self.num_anchors[i], 1, 1, 0)]

      if arch == 'ssd':
        reg_conv += [nn.Conv2d(chs, 4 * self.num_anchors[i], 3, 1, 1)]
        cls_conv += [nn.Conv2d(chs, num_classes * self.num_anchors[i], 3, 1, 1)]

      if arch == 'tiny-dsod':
        cchs, chs4 = num_classes * self.num_anchors[i], self.num_anchors[i] * 4
        reg_conv += [nn.Conv2d(chs4, chs4, 3, 1, 1, groups=chs4, bias=False), nn.BatchNorm2d(chs)]
        cls_conv += [nn.Conv2d(cchs, cchs, 3, 1, 1, groups=cchs, bias=False), nn.BatchNorm2d(chs)]

      reg_convs.append(nn.Sequential(*reg_conv))
      cls_convs.append(nn.Sequential(*cls_conv))

    # module
    self.reg_convs = nn.ModuleList(reg_convs)
    self.cls_convs = nn.ModuleList(cls_convs)

    # reset
    self.reset_parameters()

  def reset_parameters(self):
    for m in self.modules():
      if isinstance(m, nn.Conv2d):
        tw.nn.initialize.kaiming(m)
      elif isinstance(m, nn.BatchNorm2d):
        tw.nn.initialize.constant(m, 1)
      elif isinstance(m, nn.Linear):
        tw.nn.initialize.normal(m, std=0.01)

  def forward(self, feats):
    """BBox Head for SSD model.

    Args:
        feats (list[Tensor]): extracted from backbones network.

    Returns:
        bbox_cls (list[Tensor]): [n, classes * anc, h, w]
        bbox_reg (list[Tensor]): [n, 4 * anc, h, w]
    """
    bbox_cls = [self.cls_convs[i](feat) for i, feat in enumerate(feats)]
    bbox_reg = [self.reg_convs[i](feat) for i, feat in enumerate(feats)]
    return bbox_cls, bbox_reg

#!<----------------------------------------------------------------------------
#!< Yolo Head
#!<----------------------------------------------------------------------------


class RoIBoxHeadYOLO(nn.Module):
  def __init__(self, num_classes, num_anchors, input_size):
    super(RoIBoxHeadYOLO, self).__init__()
    self.num_classes = num_classes
    self.num_anchors = num_anchors
    self.input_size = input_size

  def forward(self, feats):
    """YOLO Head

    Args:
        feats: (list[Tensor]) extracted from backbones network.
            for each shape -> (bs, N_ANC * (4 + num_classes), h, w)

    Returns:
        bbox_cls (list[Tensor]): [n, anc * classes, h, w]
        bbox_reg (list[Tensor]): [n, anc * 4, h, w]
    """
    bbox_cls = []
    bbox_reg = []

    for feat in feats:
      n, _, h, w = feat.shape
      feat = feat.reshape(n, self.num_anchors, 4 + self.num_classes, h, w)
      layer_reg, layer_cls = feat.split([4, self.num_classes], dim=2)

      # output shape
      layer_cls = layer_cls.reshape(n, -1, h, w)
      layer_reg = layer_reg.reshape(n, -1, h, w)

      # append
      bbox_cls.append(layer_cls)
      bbox_reg.append(layer_reg)

    return bbox_cls, bbox_reg

#!<----------------------------------------------------------------------------
#!< FCOS Head
#!<----------------------------------------------------------------------------


class RoIBoxHeadFCOS(nn.Module):
  def __init__(self,
               num_classes=80,
               in_channels=256,
               num_convs=4):
    super(RoIBoxHeadFCOS, self).__init__()
    cls_convs = []
    reg_convs = []
    for _ in range(num_convs):
      cls_convs.extend([
          nn.Conv2d(in_channels, in_channels, 3, 1, 1, bias=True),
          nn.GroupNorm(32, in_channels),
          nn.ReLU(inplace=True)])
      reg_convs.extend([
          nn.Conv2d(in_channels, in_channels, 3, 1, 1, bias=True),
          nn.GroupNorm(32, in_channels),
          nn.ReLU(inplace=True)])
    self.cls_convs = nn.Sequential(*cls_convs)
    self.reg_convs = nn.Sequential(*reg_convs)

    # head
    self.cls_logits = nn.Conv2d(in_channels, num_classes, 3, 1, 1)
    self.bbox_pred = nn.Conv2d(in_channels, 4, 3, 1, 1)
    self.centerness = nn.Conv2d(in_channels, 1, 3, 1, 1)
    self.scales = nn.ModuleList([tw.nn.Scale(1.0) for _ in range(5)])

  def reset_parameters(self):
    for module in self.modules():
      if isinstance(module, nn.Conv2d):
        tw.nn.initialize.normal(module, std=0.01)
    prior_prob = 0.01
    bias_value = -math.log((1 - prior_prob) / prior_prob)
    torch.nn.init.constant_(self.cls_logits.bias, bias_value)

  def forward(self, feature_lists):
    bbox_cls = []
    bbox_reg = []
    centerness = []
    for layer_idx, feature in enumerate(feature_lists):
      cls_convs = self.cls_convs(feature)
      box_convs = self.reg_convs(feature)
      # head
      bbox_cls.append(self.cls_logits(cls_convs))
      centerness.append(self.centerness(cls_convs))
      bbox_pred = self.scales[layer_idx](self.bbox_pred(box_convs))
      bbox_reg.append(torch.exp(bbox_pred))
    return bbox_cls, bbox_reg, centerness

#!<----------------------------------------------------------------------------
#!< RetinaNet Head
#!<----------------------------------------------------------------------------


class RoIBoxHeadRetinaNet(nn.Module):

  def __init__(self, num_classes=80, in_channels=256, out_channels=256, num_anchors=9, num_convs=4):
    super(RoIBoxHeadRetinaNet, self).__init__()
    self.cls_convs = nn.ModuleList()
    self.reg_convs = nn.ModuleList()
    for i in range(num_convs):
      chn = in_channels if i == 0 else out_channels
      self.cls_convs.append(ConvModule(nn.Conv2d(chn, out_channels, 3, stride=1, padding=1), act=nn.ReLU()))
      self.reg_convs.append(ConvModule(nn.Conv2d(chn, out_channels, 3, stride=1, padding=1), act=nn.ReLU()))
    self.retina_cls = nn.Conv2d(out_channels, num_anchors * num_classes, 3, padding=1)
    self.retina_reg = nn.Conv2d(out_channels, num_anchors * 4, 3, padding=1)
    self.reset_parameters()

  def reset_parameters(self):
    for module in self.modules():
      if isinstance(module, nn.Conv2d):
        tw.nn.initialize.normal(module, std=0.01)
    prior_prob = 0.01
    bias_value = -math.log((1 - prior_prob) / prior_prob)
    torch.nn.init.constant_(self.retina_cls.bias, bias_value)

  def forward(self, feature_lists):
    bbox_cls, bbox_reg = [], []
    for feature in feature_lists:
      cls_feat = feature
      reg_feat = feature
      for cls_conv in self.cls_convs:
        cls_feat = cls_conv(cls_feat)
      for reg_conv in self.reg_convs:
        reg_feat = reg_conv(reg_feat)
      bbox_cls.append(self.retina_cls(cls_feat))
      bbox_reg.append(self.retina_reg(reg_feat))
    return bbox_cls, bbox_reg

#!<----------------------------------------------------------------------------
#!< YOLOF Head
#!<----------------------------------------------------------------------------


class RoIBoxHeadYOLOF(nn.Module):

  """YOLOFHead Paper link: https://arxiv.org/abs/2103.09460.

  Args:
      num_classes (int): The number of object classes (w/o background)
      in_channels (List[int]): The number of input channels per scale.
      cls_num_convs (int): The number of convolutions of cls branch. Default 2.
      reg_num_convs (int): The number of convolutions of reg branch. Default 4.
  """

  def __init__(self,
               num_classes,
               in_channels,
               num_anchors,
               num_cls_convs=2,
               num_reg_convs=4,
               **kwargs):
    super(RoIBoxHeadYOLOF, self).__init__()
    self.num_classes = num_classes
    self.in_channels = in_channels
    self.num_cls_convs = num_cls_convs
    self.num_reg_convs = num_reg_convs
    self.num_anchors = num_anchors

    cls_subnet = []
    bbox_subnet = []

    for i in range(self.num_cls_convs):
      cls_subnet.append(nn.Sequential(
          nn.Conv2d(self.in_channels, self.in_channels, kernel_size=3, padding=1),
          nn.BatchNorm2d(self.in_channels)))

    for i in range(self.num_reg_convs):
      bbox_subnet.append(nn.Sequential(
          nn.Conv2d(self.in_channels, self.in_channels, kernel_size=3, padding=1),
          nn.BatchNorm2d(self.in_channels)))

    self.cls_subnet = nn.Sequential(*cls_subnet)
    self.bbox_subnet = nn.Sequential(*bbox_subnet)
    self.cls_score = nn.Conv2d(self.in_channels, self.num_anchors * self.num_classes, kernel_size=3, stride=1, padding=1)  # nopep8
    self.bbox_pred = nn.Conv2d(self.in_channels, self.num_anchors * 4, kernel_size=3, stride=1, padding=1)
    self.object_pred = nn.Conv2d(self.in_channels, self.num_anchors, kernel_size=3, stride=1, padding=1)

    for m in self.modules():
      if isinstance(m, nn.Conv2d):
        tw.nn.initialize.normal(m, mean=0, std=0.01)

    # Use prior in model initialization to improve stability
    torch.nn.init.constant_(self.cls_score.bias, float(-np.log((1 - 0.01) / 0.01)))

  def forward(self, feature):
    """yolof only have one feature.
    """
    cls_score = self.cls_score(self.cls_subnet(feature))
    N, _, H, W = cls_score.shape
    cls_score = cls_score.view(N, -1, self.num_classes, H, W)

    reg_feat = self.bbox_subnet(feature)
    bbox_reg = self.bbox_pred(reg_feat)
    objectness = self.object_pred(reg_feat)

    # implicit objectness
    objectness = objectness.view(N, -1, 1, H, W)
    normalized_cls_score = cls_score + objectness - torch.log(1. + torch.clamp(cls_score.exp(), max=1e8) + torch.clamp(objectness.exp(), max=1e8))  # nopep8
    normalized_cls_score = normalized_cls_score.view(N, -1, H, W)
    return normalized_cls_score, bbox_reg

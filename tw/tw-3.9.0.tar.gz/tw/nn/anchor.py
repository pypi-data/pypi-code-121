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
"""anchor is a basic module in object detection.

  The main function of anchor is to mapping localization relationship between
  roi of feature map and groundtruth.

  In addition, we could encode (x1, y1, x2, y2) groundtruth into anchors.

"""
from torch import nn
import torch
import numpy as np
import tw


#!<-----------------------------------------------------------------------------
#!< Generate anchors
#!<-----------------------------------------------------------------------------


def _generate_anchors(base_size, scales, aspect_ratios):
  """Generate anchor (reference) windows by enumerating aspect ratios X
  scales wrt a reference (0, 0, base_size - 1, base_size - 1) window.
  """
  anchor = np.array([1, 1, base_size, base_size], dtype=np.float) - 1
  anchors = _ratio_enum(anchor, aspect_ratios)
  anchors = np.vstack([_scale_enum(anchors[i, :], scales) for i in range(anchors.shape[0])])
  anchors = torch.from_numpy(anchors).round().type(torch.float32)
  return anchors


def _whctrs(anchor):
  """Return width, height, x center, and y center for an anchor (window)."""
  w = anchor[2] - anchor[0] + 1
  h = anchor[3] - anchor[1] + 1
  x_ctr = anchor[0] + 0.5 * (w - 1)
  y_ctr = anchor[1] + 0.5 * (h - 1)
  return w, h, x_ctr, y_ctr


def _mkanchors(ws, hs, x_ctr, y_ctr):
  """Given a vector of widths (ws) and heights (hs) around a center
  (x_ctr, y_ctr), output a set of anchors (windows).
  """
  ws = ws[:, np.newaxis]
  hs = hs[:, np.newaxis]
  anchors = np.hstack((
      x_ctr - 0.5 * (ws - 1),
      y_ctr - 0.5 * (hs - 1),
      x_ctr + 0.5 * (ws - 1),
      y_ctr + 0.5 * (hs - 1),
  ))
  return anchors


def _ratio_enum(anchor, ratios):
  """Enumerate a set of anchors for each aspect ratio wrt an anchor."""
  w, h, x_ctr, y_ctr = _whctrs(anchor)
  size = w * h
  size_ratios = size / ratios
  ws = np.sqrt(size_ratios)
  hs = ws * ratios
  anchors = _mkanchors(ws, hs, x_ctr, y_ctr)
  return anchors


def _scale_enum(anchor, scales):
  """Enumerate a set of anchors for each scale wrt an anchor."""
  w, h, x_ctr, y_ctr = _whctrs(anchor)
  ws = w * scales
  hs = h * scales
  anchors = _mkanchors(ws, hs, x_ctr, y_ctr)
  return anchors


#!<-----------------------------------------------------------------------------
#!< Anchor base utils
#!<-----------------------------------------------------------------------------

def generate_anchors(stride=16, sizes=(32, 64, 128, 256, 512), aspect_ratios=(0.5, 1, 2)):
  """Generates a matrix of anchor boxes in (x1, y1, x2, y2) format. Anchors
    are centered on stride / 2, have (approximate) sqrt areas of the specified
    sizes, and aspect ratios as given.
  """
  return _generate_anchors(stride,
                           np.array(sizes, dtype=np.float) / stride,
                           np.array(aspect_ratios, dtype=np.float))


def generate_grids(generators, feature_lists, img_h, img_w):
  """According the width and height of feature lists to dynamically generate
    anchors.

  Args:
      generators ([type]): [general anchor generator list]
      feature_lists ([type]): [[h1, w1], [h2, w2], [h3, w3]] from high to low resolution.
      img_h ([type]): [clamp to img_h]
      img_w ([type]): [clamp to img_w]

  Returns:
      [tensor]: [anchors]
  """
  anchors = []
  for idx, feature_size in enumerate(feature_lists):  # [H, W]
    anchor = generators[idx](*feature_size)
    # clamp to (0, 0, w, h)
    anchor = torch.stack(
        [
            anchor[..., 0].clamp(min=0),
            anchor[..., 1].clamp(min=0),
            anchor[..., 2].clamp(max=img_w),
            anchor[..., 3].clamp(max=img_h),
        ],
        dim=-1)
    anchors.append(anchor)
  return anchors


#!<-----------------------------------------------------------------------------
#!< General Anchor Generator
#!<-----------------------------------------------------------------------------

class GeneralAnchorGenerator(nn.Module):

  def __init__(self, stride=8,
               sizes=[32, 64, 128, 256, 512],
               ratios=[0.5, 1, 2],
               straddle_thresh=0):
    """For a set of image sizes and feature maps, computes a set of anchors.
      Anchor is a cropped window on images. Due to cropping from feature maps
      with different scales, we should generate a series of anchors that are
      corresponding to the coordinate on the images.

    Args:
        stride (int, optional): [description]. Defaults to 8.
        sizes (list, optional): [description]. Defaults to [32, 64, 128, 256, 512].
        ratios (list, optional): [description]. Defaults to [0.5, 1, 2].
        straddle_thresh (int, optional): [description]. Defaults to 0.

    """
    super(GeneralAnchorGenerator, self).__init__()
    # print('stride:{}\nsizes:{}\nratios:{}\n'.format(stride, sizes, ratios))
    self.stride = stride
    self.straddle_thresh = straddle_thresh

    # register to buffer in order to easily moving on different device
    self.register_buffer('anchors', generate_anchors(stride, sizes, ratios))

  def forward(self, fh, fw):
    """Generate anchors over h and w, it only generate cropped coordinates
      instead of the values. So, we need only the sizes.

    Args:
        fh ([int]): [description]
        fw ([int]): [description]

    NOTE:
      we assume each feature layer have an anchor generator in order to meet
    different detection method, given that the different anchor configuration.

    TODO:
      we could cache the anchors corresponding to various image sizes for training.

    """
    shifts_x = torch.arange(0, fw * self.stride, step=self.stride, dtype=torch.float32)
    shifts_y = torch.arange(0, fh * self.stride, step=self.stride, dtype=torch.float32)

    # meshgrid, MxN
    shift_y, shift_x = torch.meshgrid(shifts_y, shifts_x)
    shift_x = shift_x.reshape(-1)
    shift_y = shift_y.reshape(-1)

    # x1y1x1y1
    shifts = torch.stack((shift_x, shift_y, shift_x, shift_y), dim=1).to(self.anchors.device)

    # add width and height
    # for a feature map, the number of points is fh*fw = N
    # each points use sizes * ratio anchors = C
    # so, the total anchors is N * C
    # [N, 1, 4] + [1, C, 4] -> [N, C, 4] -> [N*C, 4]
    anchors = shifts.view(-1, 1, 4) + self.anchors.view(1, -1, 4)
    anchors = anchors.reshape(-1, 4)
    return anchors

#!<-----------------------------------------------------------------------------
#!< RetinaNet Anchor Generator
#!<-----------------------------------------------------------------------------


class SSDAnchorGenerator(nn.Module):
  """See: SSD: Single shot multibox detector
  """

  def __init__(self, input_size=320,
               anchor_strides=(8, 16, 32, 64, 100, 300),
               basesize_ratio_range=(0.15, 0.9),
               anchor_ratios=([2], [2, 3], [2, 3], [2, 3], [2], [2]),
               straddle_thresh=0.0):
    """[summary]

    Args:
        input_size (int, optional): [description]. Defaults to 320.
        anchor_strides (tuple, optional): [description]. Defaults to (8, 16, 32, 64, 100, 300).
        basesize_ratio_range (tuple, optional): [description]. Defaults to (0.15, 0.9).
        anchor_ratios (tuple, optional): [description]. Defaults to ([2], [2, 3], [2, 3], [2, 3], [2], [2]).
        straddle_thresh (float, optional): [description]. Defaults to 0.0.
    """
    super(SSDAnchorGenerator, self).__init__()
    assert len(anchor_ratios) == len(anchor_strides), "number of sizes and strides should be same."

    # check input
    if isinstance(input_size, list):
      input_size = input_size[1]

    # multiply 100 to make an int.
    min_ratio, max_ratio = basesize_ratio_range
    min_ratio = int(min_ratio * 100)
    max_ratio = int(max_ratio * 100)

    # (s_max - s_min) / (m - 1), while m represents the number of feature map layers, the first layer is independently set.
    if len(anchor_strides) <= 2:
      min_sizes = [(input_size * min_ratio), ]
      max_sizes = [(input_size * max_ratio), ]
    else:
      step = int(np.floor(max_ratio - min_ratio) / (len(anchor_strides) - 2))
      min_sizes = []
      max_sizes = []
      # s_r = s_min + step * r
      for r in range(int(min_ratio), int(max_ratio) + 1, step):
        min_sizes.append((input_size * r / 100.))
        max_sizes.append((input_size * (r + step) / 100.))

    # independently setting the first layer
    # its scale is s_min / 2
    if input_size == 512:
      if basesize_ratio_range[0] == 0.1:  # COCO
        min_sizes.insert(0, (input_size * 4 / 100.))
        max_sizes.insert(0, (input_size * 10 / 100.))
      elif basesize_ratio_range[0] == 0.15:  # VOC
        min_sizes.insert(0, (input_size * 7 / 100.))
        max_sizes.insert(0, (input_size * 15 / 100.))
      else:
        raise NotImplementedError(basesize_ratio_range[0])
    else:
      if basesize_ratio_range[0] == 0.15:  # COCO
        min_sizes.insert(0, (input_size * 7 / 100.))
        max_sizes.insert(0, (input_size * 15 / 100.))
      elif basesize_ratio_range[0] == 0.2:  # VOC
        min_sizes.insert(0, (input_size * 10 / 100.))
        max_sizes.insert(0, (input_size * 20 / 100.))
      else:
        raise NotImplementedError(basesize_ratio_range[0])

    # setting anchor generator
    # due to ssd use different anchors for different layer, we need set a
    # series of AnchorGenerator.
    generators = []
    for k, stride in enumerate(anchor_strides):
      ratios = []
      # NOTE: e.g. [2, 3] -> [1, 1/2, 2, 1/3, 3]
      for r in anchor_ratios[k]:
        ratios += [1. / r, r]
      # because only the first layer only two sizes, others use one.
      anchor_generator_layer1 = GeneralAnchorGenerator(
          stride=stride,
          sizes=(min_sizes[k], min_sizes[k] * np.sqrt(max_sizes[k] / min_sizes[k])),
          ratios=[1., ],
          straddle_thresh=straddle_thresh)
      anchor_generator = GeneralAnchorGenerator(
          stride=stride,
          sizes=(min_sizes[k],),
          ratios=ratios,
          straddle_thresh=straddle_thresh)
      anchor_generator.anchors = torch.cat([anchor_generator_layer1.anchors,
                                            anchor_generator.anchors],
                                           dim=0)
      generators.append(anchor_generator)
    self.generators = nn.ModuleList(generators)

  def __len__(self):
    return len(self.generators)

  def __getitem__(self, idx):
    return self.generators[idx]

  def forward(self, feature_sizes, img_h, img_w):
    return generate_grids(self.generators, feature_sizes, img_h, img_w)


#!<-----------------------------------------------------------------------------
#!< RetinaNet Anchor Generator
#!<-----------------------------------------------------------------------------


class RetinaNetAnchorGenerator(nn.Module):
  """See: Focal Loss for Dense Object Detection
  """

  def __init__(self, anchor_sizes=[32, 64, 128, 256, 512],
               anchor_strides=[8, 16, 32, 64, 128],
               anchor_ratios=[0.5, 1.0, 2.0],
               straddle_thresh=0.0,
               octave=2.0,
               scales_per_octave=3):
    """[summary]

    Args:
        anchor_sizes (list, optional): [description]. Defaults to [32, 64, 128, 256, 512].
        anchor_strides (list, optional): [description]. Defaults to [8, 16, 32, 64, 128].
        anchor_ratios (list, optional): [description]. Defaults to [0.5, 1.0, 2.0].
        straddle_thresh (float, optional): [description]. Defaults to 0.0.
        octave (float, optional): [description]. Defaults to 2.0.
        scales_per_octave (int, optional): [description]. Defaults to 3.
        device ([type], optional): [description]. Defaults to None.

    """
    super(RetinaNetAnchorGenerator, self).__init__()
    assert len(anchor_sizes) == len(anchor_strides), "number of sizes and strides should be same."

    # see paper: 4 sub-octave scales: 2^{k/4} for k <= 3
    # each location yield 12 base box: 4 sub-octave size and 3 aspect ratio.
    new_anchor_sizes = []
    for size in anchor_sizes:
      per_layer_anchor_sizes = []
      for scale_per_octave in range(scales_per_octave):
        octave_scale = octave ** (scale_per_octave / float(scales_per_octave))
        per_layer_anchor_sizes.append(octave_scale * size)
      new_anchor_sizes.append(tuple(per_layer_anchor_sizes))

    generators = []
    self.anchor_strides = anchor_strides
    for sizes, stride in zip(new_anchor_sizes, anchor_strides):
      generators.append(GeneralAnchorGenerator(
          stride=stride,
          sizes=sizes,
          ratios=anchor_ratios,
          straddle_thresh=straddle_thresh))
    self.generators = nn.ModuleList(generators)

  def __len__(self):
    return len(self.generators)

  def __getitem__(self, idx):
    return self.generators[idx]

  def forward(self, feature_sizes, img_h, img_w):
    return generate_grids(self.generators, feature_sizes, img_h, img_w)


#!<-----------------------------------------------------------------------------
#!< RetinaFace Anchor Generator
#!<-----------------------------------------------------------------------------


class RetinaFaceAnchorGenerator(nn.Module):
  """See: RetinaFace: Single-shot Multi-level Face Localisation in the Wild
  """

  def __init__(self, anchor_sizes=[[32, 64], [64, 128], [128, 256]],
               anchor_strides=[8, 16, 32],
               anchor_ratios=[1.0, ],
               straddle_thresh=0.0):
    """RetinaFace anchor setting, referred by github.

    Args:
        anchor_sizes (list, optional): [description]. Defaults to [[32, 64], [64, 128], [128, 256]].
        anchor_strides (list, optional): [description]. Defaults to [8, 16, 32].
        anchor_ratios (list, optional): [description]. Defaults to [1.0, ].
        straddle_thresh (float, optional): [description]. Defaults to 0.0.

    """
    super(RetinaFaceAnchorGenerator, self).__init__()
    assert len(anchor_sizes) == len(anchor_strides), "number of sizes and strides should be same."

    generators = []
    self.anchor_strides = anchor_strides
    for sizes, stride in zip(anchor_sizes, anchor_strides):
      generators.append(GeneralAnchorGenerator(
          stride=stride,
          sizes=sizes,
          ratios=anchor_ratios,
          straddle_thresh=straddle_thresh))
    self.generators = nn.ModuleList(generators)

  def __len__(self):
    return len(self.generators)

  def __getitem__(self, idx):
    return self.generators[idx]

  def forward(self, feature_sizes, img_h, img_w):
    return generate_grids(self.generators, feature_sizes, img_h, img_w)


#!<-----------------------------------------------------------------------------
#!< Anchor Matcher
#!<-----------------------------------------------------------------------------


class AnchorMatcher():
  """Affine target bounding box to Anchor for training. ach proposals will be
    assigned with `-1`, `0`, or a positive integer indicating the ground truth index.

    - -1: don't care
    - 0: negative sample, no assigned gt
    - positive integer: positive sample, index (1-based) of assigned gt

  """

  def __init__(self,
               pos_iou_thr=0.7,  # pos->1 -> positive int -> postive sample
               neg_iou_thr=0.3,  # 0~neg -> 0 -> negative sample
               min_pos_iou=0.0):
    self._pos_iou_thr = pos_iou_thr
    self._neg_iou_thr = neg_iou_thr
    self._min_pos_iou = min_pos_iou

  def __call__(self, anchors, gt_bboxes, gt_labels=None):
    """
    Arguments:
      anchors (Tensor) [N, 4]: Bounding boxes to be assigned.
      gt_bboxes (Tensor) [K, 4]: Groundtruth boxes.
      gt_labels (Tensor) [K]: Label of gt_bboxes.

    Returns:
      assigned_gt_inds (Tensor) [N,]: each anchor is coressponding to someone gt bboxes index. (1-based)
      assigned_label (Tensor) [N,]: each anchor is corressponding to someone gt labels.

    """

    # consider without any gt (is crowd)
    n_anchors = anchors.size(0)
    assigned_gt_inds = anchors.new_full((n_anchors,), -1, dtype=torch.long)
    assigned_label = assigned_gt_inds.new_zeros((n_anchors, ))

    if gt_bboxes.size(0) == 0:
      return assigned_gt_inds, assigned_label

    if gt_bboxes.size(0) != gt_labels.size(0):
      raise ValueError(gt_bboxes.size(0), gt_labels.size(0))

    # computing IoU between anchors and gt_bboxes
    overlaps = tw.transform.bbox.iou(gt_bboxes, anchors)
    num_gts, num_bboxes = overlaps.size(0), overlaps.size(1)

    # for each anchor, it finds best suitable groundtruth bboxes. # [N, ]
    max_overlaps, argmax_overlaps = overlaps.max(dim=0)
    # for each groundtruth, it finds best suitable anchors. # [K, ]
    gt_max_overlaps, gt_argmax_overlaps = overlaps.max(dim=1)

    # assign negative sample: with minor overlapping with groundtruth
    neg_inds = (max_overlaps >= 0) & (max_overlaps < self._neg_iou_thr)
    assigned_gt_inds[neg_inds] = 0

    # assign positive sample
    pos_inds = max_overlaps >= self._pos_iou_thr
    # there is not a label value, but the corresponding gt index [1~K+1]
    assigned_gt_inds[pos_inds] = argmax_overlaps[pos_inds] + 1

    # assign fg: each target box match a best anchor
    for i in range(num_gts):
      if gt_max_overlaps[i] >= self._min_pos_iou:
        assigned_gt_inds[gt_argmax_overlaps[i]] = i + 1

    # assign labels
    if gt_labels is not None:
      assigned_label = assigned_gt_inds.new_zeros((num_bboxes,))
      # find out all positive proposals
      pos_inds = torch.nonzero(assigned_gt_inds > 0, as_tuple=False).squeeze()
      if pos_inds.numel() > 0:
        assigned_label[pos_inds] = gt_labels[assigned_gt_inds[pos_inds] - 1]
    else:
      assigned_label = None

    return assigned_gt_inds, assigned_label

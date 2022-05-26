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
"""Keypoints Coder and Decoder
"""
import abc
import math
import torch
import numpy as np
import tw

#!<-----------------------------------------------------------------------------
#!< Base Pts Coder
#!<-----------------------------------------------------------------------------


class _BasePtsCoder(abc.ABC):
  """PtsCoder is a technical to regress the deltas from network outputs.
  """
  @abc.abstractmethod
  def encode(self, references, proposals):
    """Encode a set of proposals with respect to some reference Ptses"""
    raise NotImplementedError

  @abc.abstractmethod
  def decode(self, encodes, anchors):
    """From a set of original Ptses and encoded relative Pts offsets, get the
    decoded Ptses."""
    raise NotImplementedError


class BboxPtsCoder(_BasePtsCoder):
  """Keypoints affine on bounding box.
  """

  def __init__(self,
               means=[0, 0],
               variances=[1, 1],
               bbox_xform_clip=math.log(1000. / 16),
               clamp_to_image_shape=None):
    super(BboxPtsCoder, self).__init__()
    self.means = means
    self.variances = variances
    self.bbox_xform_clip = bbox_xform_clip
    self.clamp_to_image_shape = clamp_to_image_shape

  def encode(self, references, proposals):
    """references from ground truth, proposals from positive sample.

      dx = (proposal_centered_x - gt_centered_x) / proposal_width
      dy = (proposal_centered_y - gt_centered_y) / proposal_height
      deltas = ([dx, dy] - means) / variances

    Args:
        references ([N, 2(x1, y1, x2, y2, ...)]): groundtruth of keypoints
        proposals ([N, 4(x1, y1, x2, y2)]): anchors of bounding box

    Returns:
        [type]: [deltas (N, 2(&x1, &y1, &x2, &y2, ...))]: normalized xy
    """
    assert proposals.size(0) == references.size(0)
    bs, npts = references.shape

    references = torch.reshape(references, (bs, npts // 2, 2))  # [N, pair, 2]
    proposals = proposals.float()

    # proposals from xyxy to centered-xywh
    px = torch.unsqueeze((proposals[..., 0] + proposals[..., 2]) * 0.5, dim=-1)
    py = torch.unsqueeze((proposals[..., 1] + proposals[..., 3]) * 0.5, dim=-1)
    pw = torch.unsqueeze(proposals[..., 2] - proposals[..., 0] + 1.0, dim=-1)
    ph = torch.unsqueeze(proposals[..., 3] - proposals[..., 1] + 1.0, dim=-1)

    # groundtruth points
    gx = references[..., 0]
    gy = references[..., 1]

    # encode
    dx = (gx - px) / pw  # delta(x) / gt-w
    dy = (gy - py) / ph  # delta(y) / gt-h
    deltas = torch.stack([dx, dy], dim=-1)

    means = deltas.new_tensor(self.means).unsqueeze(0)
    variances = deltas.new_tensor(self.variances).unsqueeze(0)
    deltas = deltas.sub_(means).div_(variances)

    return deltas.reshape(bs, -1)

  def decode(self, encodes, anchors):
    """decode network outputs in terms of anchors. The processing is an inverse
      process compared with encoding.

      denorm_deltas = deltas * variances + means
      denorm_deltas [dx, dy]

      px = (anchor_x1 + anchor_x2) / 2
      py = (anchor_y1 + anchor_y2) / 2
      pw = (anchor_x2 - anchor_x1) + 1
      ph = (anchor_y2 - anchor_y1) + 1

      gx = px + pw * dx
      gy = py + ph * dy

      x1 = gx - gw * 0.5 + 0.5
      y1 = gy - gh * 0.5 + 0.5

      prediction bbox [x1, y1, ...]

    Args:
        encodes ([type]): [network output pts, (N, pair*2)]
        anchors ([type]): [anchors, (N, 4)]

    Returns:
        [type]: [prediction pts (N, pair, 2)]

    """
    bs, npts = encodes.shape
    device = encodes.device

    # [bs, num-pair, 2]
    encodes = encodes.reshape(bs, npts // 2, 2)
    variances = torch.tensor(self.variances).to(device)
    means = torch.tensor(self.means).to(device)
    denorm_deltas = encodes * variances + means

    dx = denorm_deltas[..., 0]
    dy = denorm_deltas[..., 1]

    px = ((anchors[:, 0] + anchors[:, 2]) * 0.5).reshape(bs, 1)
    py = ((anchors[:, 1] + anchors[:, 3]) * 0.5).reshape(bs, 1)
    pw = (anchors[:, 2] - anchors[:, 0] + 1.0).reshape(bs, 1)
    ph = (anchors[:, 3] - anchors[:, 1] + 1.0).reshape(bs, 1)
    gx = px + pw * dx
    gy = py + ph * dy

    if self.clamp_to_image_shape is not None:
      gx = gx.clamp(min=0, max=self.clamp_to_image_shape[1] - 1)
      gy = gy.clamp(min=0, max=self.clamp_to_image_shape[0] - 1)

    pts = torch.stack([gx, gy], dim=-1)
    return pts

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
r"""nms related
"""

import torch

try:
  from tw import _C
except ImportError:
  _C = None


def nms(preds, thresh):
  """nms c++/cuda impl.

  Args:
      preds ([type]): [description]
      thresh ([type]): [description]

  Returns:
      [type]: [description]
  """
  return _C.nms(preds, thresh)


class NonMaxSuppression(torch.nn.Module):

  def forward(self, preds, thresh, max_proposals=0):
    r"""NMS Inference

    Args:
      preds (Tensor[N, 5]): x1, y1, x2, y2, conf
      thresh (float [0, 1]):

    """
    if thresh < 0:
      return preds
    keep = nms(preds, thresh)
    if max_proposals > 0:
      keep = keep[: max_proposals]
    return preds[keep], keep


class MultiLabelNonMaxSuppression(torch.nn.Module):

  def forward(self, boxes, scores, labels, thresh, max_proposals=0):
    r"""ML-NMS Inference

    Args:
      boxes (Tensor[N, 4]): x1, y1, x2, y2
      scores (Tensor[N]):
      labels (Tensor[N]):
      thresh (float [0, 1]):

    """
    if thresh < 0:
      return boxes
    keep = _C.ml_nms(boxes, scores, labels.float(), thresh)
    if max_proposals > 0:
      keep = keep[: max_proposals]
    return boxes[keep], keep


class MulticlassNMS(torch.nn.Module):
  def __init__(self, nms_type='nms', background_offset=1):
    super(MulticlassNMS, self).__init__()
    self.background_offset = background_offset
    self.nms_type = nms_type
    if nms_type in ['nms']:
      self.nms = NonMaxSuppression()
    else:
      raise NotImplementedError

  def forward(self, bboxes, scores, conf_thresh, nms_thresh, max_instances=0):
    r"""NMS for multiclass bboxes
      NOTE: for multiclass-sigmoid scores, the maximum score (label) is its
      score, other should be set to zero (box_inference).

    Args:
      bboxes (Tensor): [N, 4]
      scores (Tensor): [N, num_classes]
      conf_thresh (float): bboxes with scores lower will not be considered.
      nms_thresh (float): higher the thresh will be merged.

    Returns:
      tuple: (bboxes, labels): tensors of shape (k, 5) and (k, 1).

    """
    if scores.numel() == 0:
      preds = bboxes.new_zeros((0, 5))
      labels = bboxes.new_zeros((0, ), dtype=torch.long)
      return preds, labels

    num_classes = scores.size(1)
    preds = []
    labels = []

    # assuming 0 is the background
    # independently processing for each classification
    for i in range(self.background_offset, num_classes):
      inds = scores[:, i] > conf_thresh
      if not inds.any():
        continue

      bbox = bboxes[inds, :]  # [M, 4]
      score = scores[inds, i]  # [M]
      pred = torch.cat([bbox, score[:, None]], dim=1)  # [M, 5]
      pred, _ = self.nms(pred, nms_thresh)
      label = bboxes.new_full((pred.shape[0], ), i, dtype=torch.long)
      labels.append(label)
      preds.append(pred)

    # merging
    if preds:
      preds, labels = torch.cat(preds), torch.cat(labels)
      if max_instances > 0:
        # last value represent score
        _, inds = preds[:, -1].sort(descending=True)
        inds = inds[:max_instances]
        preds = preds[inds]
        labels = labels[inds]
    else:
      preds = bboxes.new_zeros((0, 5))
      labels = bboxes.new_zeros((0, ), dtype=torch.long)

    return preds, labels

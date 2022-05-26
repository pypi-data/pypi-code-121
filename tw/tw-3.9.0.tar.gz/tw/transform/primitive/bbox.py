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
"""BoundingBox Tensor Operation
"""
import torch
import math
import tw


def remove_small_boxes(boxes, min_h, min_w):
  """Remove boxes which contains at least one side smaller than min_size.

  Args:
      boxes (Tensor[N, 4]): boxes in [x0, y0, x1, y1] format
      min_size (int): minimum size

  Returns:
      keep (Tensor[K]): indices of the boxes that have both sides larger than min_size
  """
  assert isinstance(boxes, torch.Tensor)
  ws, hs = boxes[:, 2] - boxes[:, 0], boxes[:, 3] - boxes[:, 1]
  keep = (ws >= min_w) & (hs >= min_h)
  keep = keep.nonzero().squeeze(1)
  return keep


def clamp_to_image(boxes, img_h, img_w):
  """Clamp boxes so that they lie inside an image of size `size`.

  Args:
      boxes: Tensor([N, 4]) x1, y1, x2, y2
      img_h: (int)
      img_w: (int)

  Returns:
    boxes: Tensor(N, 4)
  """
  assert isinstance(boxes, torch.Tensor)
  boxes_x = boxes[..., 0::2]
  boxes_y = boxes[..., 1::2]
  boxes_x = boxes_x.clamp(min=0, max=img_w)
  boxes_y = boxes_y.clamp(min=0, max=img_h)
  clipped_boxes = torch.stack((boxes_x, boxes_y), dim=-1)
  return clipped_boxes.reshape(boxes.shape)


def area(boxes):
  """Computes the area of a set of bounding boxes, which are specified by its
    (x0, y0, x1, y1) coordinates.

  Args:
      boxes (Tensor[N, 4]): boxes for which the area will be computed. They
          are expected to be in (x0, y0, x1, y1) format

  Returns:
      area (Tensor[N]): area for each box
  """
  assert isinstance(boxes, torch.Tensor)
  return (boxes[:, 2] - boxes[:, 0] + 1) * (boxes[:, 3] - boxes[:, 1] + 1)


def iou(boxes1, boxes2):
  """Return intersection-over-union (Jaccard index) of boxes.

  Args:
      boxes1 (Tensor[N, 4])
      boxes2 (Tensor[M, 4])

  Returns:
      iou (Tensor[N, M]): the NxM matrix containing the pairwise IoU values for
        every element in boxes1 and boxes2
  """
  assert isinstance(boxes1, torch.Tensor)
  assert isinstance(boxes2, torch.Tensor)
  area1 = area(boxes1)
  area2 = area(boxes2)
  lt = torch.max(boxes1[:, None, :2], boxes2[:, :2])  # [N, M, 2]
  rb = torch.min(boxes1[:, None, 2:], boxes2[:, 2:])  # [N, M, 2]
  wh = (rb - lt + 1).clamp(min=0)  # [N, M, 2]
  inter = wh[:, :, 0] * wh[:, :, 1]  # [N, M]
  iou = inter / (area1[:, None] + area2 - inter)
  return iou


def aligned_iou(boxes1, boxes2, mode='iou'):
  """Return aligned intersection-over-union (Jaccard index) of boxes.

  Args:
      boxes1 (Tensor[N, 4])
      boxes2 (Tensor[N, 4])

  Returns:
      iou (Tensor[n]): the N matrix containing the pairwise IoU values for
        every element in boxes1 and boxes2
  """
  assert boxes1.shape == boxes2.shape
  lt = torch.max(boxes1[:, :2], boxes2[:, :2])  # [rows, 2]
  rb = torch.min(boxes1[:, 2:], boxes2[:, 2:])  # [rows, 2]
  wh = (rb - lt + 1).clamp(min=0)  # [rows, 2]
  overlap = wh[:, 0] * wh[:, 1]  # w * h

  # area
  area1 = (boxes1[:, 2] - boxes1[:, 0] + 1) * (boxes1[:, 3] - boxes1[:, 1] + 1)
  area2 = (boxes2[:, 2] - boxes2[:, 0] + 1) * (boxes2[:, 3] - boxes2[:, 1] + 1)

  if mode == 'iou':
    return overlap / (area1 + area2 - overlap)

  elif mode == 'iof':
    return overlap / area1

  elif mode == 'giou':
    union = area1 + area2 - overlap
    ious = overlap / union
    enclosed_lt = torch.min(boxes1[:, :2], boxes2[:, :2])
    enclosed_rb = torch.max(boxes1[:, 2:], boxes2[:, 2:])
    enclosed_wh = enclosed_rb - enclosed_lt
    enclose_area = enclosed_wh[:, 0] * enclosed_wh[:, 1]
    gious = ious - (enclose_area - union) / enclose_area
    return gious

  elif mode == 'diou':
    union = area1 + area2 - overlap
    ious = overlap / union
    enclosed_lt = torch.min(boxes1[:, :2], boxes2[:, :2])
    enclosed_rb = torch.max(boxes1[:, 2:], boxes2[:, 2:])
    enclosed_wh = enclosed_rb - enclosed_lt

    enclosed_w, enclosed_h = enclosed_wh[:, 0], enclosed_wh[:, 1]
    enclose_area = enclosed_w * enclosed_h

    c2 = enclosed_w ** 2 + enclosed_h ** 2 + 1e-6
    left = (boxes2[:, 0] + boxes2[:, 2] - boxes1[:, 0] - boxes1[:, 2]) ** 2 / 4
    right = (boxes2[:, 1] + boxes2[:, 3] - boxes1[:, 1] - boxes1[:, 3]) ** 2 / 4
    rho2 = left + right

    diou = ious - rho2 / c2
    return diou

  elif mode == 'ciou':
    union = area1 + area2 - overlap
    ious = overlap / union
    enclosed_lt = torch.min(boxes1[:, :2], boxes2[:, :2])
    enclosed_rb = torch.max(boxes1[:, 2:], boxes2[:, 2:])
    enclosed_wh = enclosed_rb - enclosed_lt

    enclosed_w, enclosed_h = enclosed_wh[:, 0], enclosed_wh[:, 1]
    enclose_area = enclosed_w * enclosed_h

    c2 = enclosed_w ** 2 + enclosed_h ** 2 + 1e-6
    left = (boxes2[:, 0] + boxes2[:, 2] - boxes1[:, 0] - boxes1[:, 2]) ** 2 / 4
    right = (boxes2[:, 1] + boxes2[:, 3] - boxes1[:, 1] - boxes1[:, 3]) ** 2 / 4
    rho2 = left + right

    diou = ious - rho2 / c2

    factor = 4 / math.pi**2
    w1, h1 = boxes1[:, 2] - boxes1[:, 0], boxes1[:, 3] - boxes1[:, 1] + 1e-6
    w2, h2 = boxes2[:, 2] - boxes2[:, 0], boxes2[:, 3] - boxes2[:, 1] + 1e-6
    v = factor * torch.pow(torch.atan(w2 / h2) - torch.atan(w1 / h1), 2)
    cious = diou - v**2 / (1 - ious + v)
    return cious

  else:
    raise NotImplementedError(mode)

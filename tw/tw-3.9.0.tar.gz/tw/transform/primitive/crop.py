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
"""CROP
"""
from typing import Sequence
import math
import random
import cv2
import numpy as np
import torch
import torchvision.transforms.functional as tvf
import torchvision.transforms as tvt
import kornia
import PIL

from tw import transform as T
from tw import logger

#!<----------------------------------------------------------------------------
#!< CROP
#!<----------------------------------------------------------------------------


def _get_crop_coords(img_h, img_w, crop_h, crop_w, rh, rw):
  y1 = int((img_h - crop_h) * rh)
  y2 = y1 + crop_h
  x1 = int((img_w - crop_w) * rw)
  x2 = x1 + crop_w
  return x1, y1, x2, y2


def _random_crop_np(inputs: np.array, height, width):
  rh = random.random()
  rw = random.random()

  h, w = inputs.shape[:2]
  new_width = int(w * width) if width < 1 else width
  new_height = int(h * height) if height < 1 else height
  x1, y1, x2, y2 = _get_crop_coords(h, w, new_height, new_width, rh, rw)
  return inputs[y1:y2, x1:x2]


@T.MetaWrapper(support=[T.ImageMeta, T.BoxListMeta, T.VideoMeta, T.KpsListMeta])
def _random_crop_meta(metas: Sequence[T.MetaBase], height, width):
  rh = random.random()
  rw = random.random()

  for meta in metas:

    if isinstance(meta, T.ImageMeta):
      h, w = meta.bin.shape[:2]
      new_width = int(w * width) if width < 1 else width
      new_height = int(h * height) if height < 1 else height
      x1, y1, x2, y2 = _get_crop_coords(h, w, new_height, new_width, rh, rw)
      meta.bin = meta.bin[y1:y2, x1:x2]

    if isinstance(meta, T.VideoMeta):
      h, w = meta.bin.shape[1:3]
      new_width = int(w * width) if width < 1 else width
      new_height = int(h * height) if height < 1 else height
      x1, y1, x2, y2 = _get_crop_coords(h, w, new_height, new_width, rh, rw)
      meta.bin = meta.bin[:, y1:y2, x1:x2]

    if isinstance(meta, T.BoxListMeta):
      assert meta.is_affine_size
      new_width = int(meta.max_x * width) if width < 1 else width
      new_height = int(meta.max_y * height) if height < 1 else height
      x1, y1, x2, y2 = _get_crop_coords(meta.max_y, meta.max_x, new_height, new_width, rh, rw)
      meta.bboxes -= [x1, y1, x1, y1]
      meta.set_affine_size(new_height, new_width)
      meta.clip_with_affine_size()

    if isinstance(meta, T.KpsListMeta):
      assert meta.is_affine_size
      new_width = int(meta.max_x * width) if width < 1 else width
      new_height = int(meta.max_y * height) if height < 1 else height
      x1, y1, x2, y2 = _get_crop_coords(meta.max_y, meta.max_x, new_width, new_height, rh, rw)
      meta.keypoints -= [x1, y1]
      meta.set_affine_size(y2, x2)
      meta.clip_with_affine_size()

  return metas


def random_crop(inputs, height, width):
  """random crop, require width and height less than image

  Args:
      inputs ([type]): [description]
      width (int or float): output width, or keep ratio (0 ~ 1)
      height (int or float): output height, or keep ratio (0 ~ 1)

  Returns:
      [type]: [description]
  """
  if T.IsNumpy(inputs):
    return _random_crop_np(inputs, height, width)
  elif T.IsMeta(inputs):
    return _random_crop_meta(inputs, height, width)
  elif T.IsTensor(inputs):
    return kornia.augmentation.RandomCrop(size=(height, width))(inputs)
  elif T.IsPilImage(inputs):
    return tvt.RandomCrop(size=(height, width))(inputs)


#!<----------------------------------------------------------------------------
#!< CENTER CROP
#!<----------------------------------------------------------------------------

def _get_center_crop_coords(height, width, crop_height, crop_width):
  y1 = (height - crop_height) // 2
  y2 = y1 + crop_height
  x1 = (width - crop_width) // 2
  x2 = x1 + crop_width
  return x1, y1, x2, y2


def _center_crop_np(inputs: np.array, height, width):
  h, w = inputs.shape[:2]
  x1, y1, x2, y2 = _get_center_crop_coords(h, w, height, width)
  return inputs[y1:y2, x1:x2]


@T.MetaWrapper(support=[T.ImageMeta, T.BoxListMeta, T.VideoMeta, T.KpsListMeta])
def _center_crop_meta(metas: Sequence[T.MetaBase], height, width):

  for meta in metas:

    if isinstance(meta, T.ImageMeta):
      h, w = meta.bin.shape[:2]
      x1, y1, x2, y2 = _get_center_crop_coords(h, w, height, width)
      meta.bin = meta.bin[y1:y2, x1:x2]

    if isinstance(meta, T.VideoMeta):
      h, w = meta.bin.shape[1:3]
      x1, y1, x2, y2 = _get_center_crop_coords(h, w, height, width)
      meta.bin = meta.bin[:, y1:y2, x1:x2]

    if isinstance(meta, T.BoxListMeta):
      assert meta.is_affine_size
      x1, y1, x2, y2 = _get_center_crop_coords(meta.max_y, meta.max_x, height, width)
      meta.bboxes -= [x1, y1, x1, y1]
      meta.set_affine_size(height, width)
      meta.clip_with_affine_size()

    if isinstance(meta, T.KpsListMeta):
      assert meta.is_affine_size
      x1, y1, x2, y2 = _get_center_crop_coords(meta.max_y, meta.max_x, height, width)
      meta.keypoints -= [x1, y1]
      meta.set_affine_size(height, width)
      meta.clip_with_affine_size()

  return metas


def center_crop(inputs, height, width):
  """crop inputs to target height and width.

  Args:
      inputs ([type]): [description]
      height ([type]): [description]
      width ([type]): [description]

  Returns:
      [type]: [description]
  """
  if T.IsNumpy(inputs):
    return _center_crop_np(inputs, height, width)
  elif T.IsMeta(inputs):
    return _center_crop_meta(inputs, height, width)
  elif T.IsTensor(inputs):
    return kornia.augmentation.CenterCrop(size=(height, width))(inputs)
  elif T.IsPilImage(inputs):
    return tvt.CenterCrop(size=(height, width))(inputs)

#!<----------------------------------------------------------------------------
#!< UTILS
#!<----------------------------------------------------------------------------


def matrix_iof(a, b):
  """return iof of a and b
  """
  lt = np.maximum(a[:, np.newaxis, :2], b[:, :2])
  rb = np.minimum(a[:, np.newaxis, 2:], b[:, 2:])

  area_i = np.prod(rb - lt, axis=2) * (lt < rb).all(axis=2)
  area_a = np.prod(a[:, 2:] - a[:, :2], axis=1)
  return area_i / np.maximum(area_a[:, np.newaxis], 1)


def matrix_iou(a, b):
  """return iou of a and b
  """
  lt = np.maximum(a[:, np.newaxis, :2], b[:, :2])
  rb = np.minimum(a[:, np.newaxis, 2:], b[:, 2:])

  area_i = np.prod(rb - lt, axis=2) * (lt < rb).all(axis=2)
  area_a = np.prod(a[:, 2:] - a[:, :2], axis=1)[:, np.newaxis]
  area_b = np.prod(b[:, 2:] - b[:, :2], axis=1)

  return area_i / (area_a + area_b - area_i)

#!<----------------------------------------------------------------------------
#!< Minimum IoU Random Crop
#!<----------------------------------------------------------------------------


@T.MetaWrapper(support=[T.ImageMeta, T.BoxListMeta, T.KpsListMeta])
def _minimum_iou_random_crop_meta(metas, min_ious, min_crop_size, **kwargs):

  # checking inputs
  assert isinstance(min_ious, (list, tuple)) and len(min_ious) >= 1
  assert min_crop_size > 0 and min_crop_size < 1

  # checking boxlist
  has_boxlist_meta, idx = False, 0
  width, height = 0, 0
  for i, meta in enumerate(metas):
    if isinstance(meta, T.BoxListMeta):
      has_boxlist_meta, idx = True, i
    if isinstance(meta, T.ImageMeta):
      width, height = meta.w, meta.h

  if not has_boxlist_meta:
    raise "MetaList must to have a BoxListMeta."
  assert width > 0 and height > 0, "valid image size."

  # finding suitable crop coordinates
  x, y, w, h = 0, 0, 0, 0
  find, mask = False, None

  # select a iou
  min_ious = (1, *min_ious, 0)

  while True:

    min_iou = random.choice(min_ious)

    # 1. min_iou is larger than 1
    # 2. current image without any bbox
    if min_iou >= 1 or len(metas[idx].bboxes) == 0:
      return metas

    # searching
    for _ in range(50):

      # random select a area
      w = random.uniform(min_crop_size * width, width)
      h = random.uniform(min_crop_size * height, height)

      # h / w in [0.5, 2] -> fit ratio of height and width
      if h / w > 0.5 and h / w < 2:
        break

      # pinpoint x, y
      x = random.uniform(0, width - w)
      y = random.uniform(0, height - h)
      roi = np.array([x, y, x + w, y + h])

      # skip roi area <= 0
      if roi[2] == roi[0] or roi[3] == roi[1]:
        continue

      # compute iou [1, 4] and [K, 4] [1, K]
      overlaps = matrix_iou(roi[np.newaxis], metas[idx].bboxes)
      if overlaps.min() < min_iou:
        continue

      # keep bbox if its center point inner patch
      centers = (metas[idx].bboxes[..., :2] + metas[idx].bboxes[..., 2:]) / 2.0

      # condition: roi_lt < centers < roi_rb [N, 2]
      mask = np.logical_and(roi[:2] < centers, centers < roi[2:])
      mask = mask.all(axis=1)  # all condition to meet

      # without any faces
      if np.sum(mask) < 1:
        continue

      # find a case
      find = True
      break

    # without suitable patches
    if find:
      break

  # to integral
  x, y, w, h = int(x), int(y), int(w), int(h)

  # using found patches as object
  for meta in metas:

    if isinstance(meta, T.ImageMeta):
      meta.bin = meta.bin[y:y + h, x:x + w]

    if isinstance(meta, T.BoxListMeta):
      assert meta.is_affine_size
      if meta.label:
        meta.label = np.array(meta.label)[mask]
      meta.bboxes = meta.bboxes[mask]
      meta.bboxes -= [x, y, x, y]
      meta.set_affine_size(h, w)
      meta.clip_with_affine_size()

    if isinstance(meta, T.KpsListMeta):
      assert meta.is_affine_size
      meta.keypoints = meta.keypoints.reshape(mask.shape[0], -1, 2)[mask]
      meta.keypoints = meta.keypoints.reshape(-1, 2)
      meta.keypoints -= [x, y]
      meta.set_affine_size(h, w)
      meta.clip_with_affine_size()

  return metas


def minimum_iou_random_crop(inputs,
                            min_ious=(0.1, 0.3, 0.5, 0.7, 0.9, 1.0),
                            min_crop_size=0.3,
                            **kwargs):
  """Random crop the image & bboxes, the cropped patches have minimum IoU
    requirement with original image & bboxes, the IoU threshold is randomly
    selected from min_ious.

  Args:
      inputs ([type]): [description]
      min_ious (tuple, optional): minimum IoU threshold for all intersections with bounding boxes
      min_crop_size (float, optional): minimum crop's size (i.e. h,w := a*h, a*w, where a >= min_crop_size).

  Note:
      The keys for bboxes, labels and masks should be paired.

  Returns:
      [type]: [description]
  """

  if T.IsNumpy(inputs):
    raise NotImplementedError
  elif T.IsMeta(inputs):
    return _minimum_iou_random_crop_meta(inputs, min_ious, min_crop_size, **kwargs)
  elif T.IsTensor(inputs):
    raise NotImplementedError
  elif T.IsPilImage(inputs):
    raise NotImplementedError


#!<----------------------------------------------------------------------------
#!< ZoomIn Square Random Crop
#!<----------------------------------------------------------------------------


@T.MetaWrapper(support=[T.ImageMeta, T.BoxListMeta, T.KpsListMeta])
def _random_zoom_in_crop_meta(metas: Sequence[T.MetaBase], scales, **kwargs):
  """composed augmentation: it through bounding box iou to iteratively sample.
  """
  # checking inputs
  assert isinstance(scales, (list, tuple)) and len(scales) >= 1

  # checking boxlist
  has_boxlist_meta, idx = False, 0
  width, height = 0, 0
  for i, meta in enumerate(metas):
    if isinstance(meta, T.BoxListMeta):
      has_boxlist_meta, idx = True, i
    if isinstance(meta, T.ImageMeta):
      width, height = meta.w, meta.h

  if not has_boxlist_meta:
    raise "MetaList must to have a BoxListMeta."
  assert width > 0 and height > 0, "valid image size."

  # finding suitable crop coordinates
  scale = 1.0
  x, y, w, h = 0, 0, 0, 0
  find, mask = False, None

  for _ in range(250):

    scale = random.choice(scales)
    short_size = min(width, height)
    w = int(scale * short_size)
    h = w  # make a square patch

    x = 0 if width == w else random.randrange(width - w)
    y = 0 if height == h else random.randrange(height - h)
    roi = np.array([x, y, x + width, y + height])

    # find at least a bounding box
    value = matrix_iof(metas[idx].bboxes, roi[np.newaxis])
    flag = value >= 1
    if not flag.any():
      continue

    # keep bbox if its center point inner patch
    centers = (metas[idx].bboxes[..., :2] + metas[idx].bboxes[..., 2:]) / 2.0

    # condition: roi_lt < centers < roi_rb [N, 2]
    mask = np.logical_and(roi[:2] < centers, centers < roi[2:])
    mask = mask.all(axis=1)  # all condition to meet

    # without any faces
    if np.sum(mask) < 1:
      continue

    # find a case
    find = True
    break

  # without suitable patches
  if not find:
    return metas

  # using found patches as object
  for meta in metas:

    if isinstance(meta, T.ImageMeta):
      meta.bin = meta.bin[y:y + h, x:x + w]

    if isinstance(meta, T.BoxListMeta):
      assert meta.is_affine_size
      if meta.label:
        meta.label = np.array(meta.label)[mask]
      meta.bboxes = meta.bboxes[mask]
      meta.bboxes -= [x, y, x, y]
      meta.set_affine_size(h, w)
      meta.clip_with_affine_size()

    if isinstance(meta, T.KpsListMeta):
      assert meta.is_affine_size
      meta.keypoints = meta.keypoints.reshape(mask.shape[0], -1, 2)[mask]
      meta.keypoints = meta.keypoints.reshape(-1, 2)
      meta.keypoints -= [x, y]
      meta.set_affine_size(h, w)
      meta.clip_with_affine_size()

  return metas


def random_zoom_in_crop(inputs, scales=[0.3, 0.45, 0.6, 0.8, 1.0], **kwargs):
  if T.IsNumpy(inputs):
    raise NotImplementedError
  elif T.IsMeta(inputs):
    return _random_zoom_in_crop_meta(inputs, scales, **kwargs)
  elif T.IsTensor(inputs):
    raise NotImplementedError
  elif T.IsPilImage(inputs):
    raise NotImplementedError

#!<----------------------------------------------------------------------------
#!< Non Overlapping Crop Patchs
#!<----------------------------------------------------------------------------


@T.MetaWrapper(support=[T.ImageMeta, ])
def _non_overlap_crop_patch_meta(metas: Sequence[T.MetaBase], patch_size=32, stride=32, **kwargs):

  # using found patches as object
  for meta in metas:

    if isinstance(meta, T.ImageMeta):
      h, w = meta.bin.shape[:2]
      patches = []
      for y in range(0, h - stride, stride):
        for x in range(0, w - stride, stride):
          patch = meta.bin[y: y + patch_size, x: x + patch_size]
          patches.append(patch)
      meta.bin = np.array(patches)

  return metas


def _non_overlap_crop_patch_tensor(inputs: torch.Tensor, patch_size=32, stride=32, **kwargs):
  c, h, w = inputs.shape
  patches = []
  for y in range(0, h - stride, stride):
    for x in range(0, w - stride, stride):
      patch = inputs[..., y: y + patch_size, x: x + patch_size]
      patches.append(patch)
  inputs = torch.stack(patches, dim=0)
  return inputs


def non_overlap_crop_patch(inputs, patch_size=32, stride=32, **kwargs):
  """non-overlapp crop.

    For a image [H, W, C], it will be divided into [N, patch_size, patch_size, C]
      N = ((h + patch_size) // (patch_size * stride)) * ((w + patch_size) // (patch_size * stride))

  Args:
      inputs ([type]): [description]
      patch_size (int, optional): [description]. Defaults to 32.
      stride (int, optional): [description]. Defaults to 32.

  Returns:
      [type]: [description]
  """
  if T.IsNumpy(inputs):
    raise NotImplementedError
  elif T.IsMeta(inputs):
    return _non_overlap_crop_patch_meta(inputs, patch_size, stride, **kwargs)
  elif T.IsTensor(inputs):
    return _non_overlap_crop_patch_tensor(inputs, patch_size, stride, **kwargs)
  elif T.IsPilImage(inputs):
    raise NotImplementedError

#!<----------------------------------------------------------------------------
#!< Crop And Padding
#!<----------------------------------------------------------------------------


@T.MetaWrapper(support=[T.ImageMeta, T.BoxListMeta])
def _random_crop_and_pad_meta(metas, target_height, target_width, fill_value=0, **kwargs):
  """process one by one.
  """
  assert target_height > 0 and target_width > 0

  for meta in metas:

    if isinstance(meta, T.ImageMeta):
      assert meta.bin.ndim == 3, "current require input to be 3-channel."
      h, w, c = meta.bin.shape

      # create a maximum image
      max_h = max(h, target_height)
      max_w = max(w, target_width)
      pad_img = np.ones([max_h, max_w, c], dtype=meta.bin.dtype) * fill_value

      # random paste
      random.seed()
      x1 = random.randint(0, max_w - w)
      y1 = random.randint(0, max_h - h)

      # paste
      pad_img[y1: y1 + h, x1: x1 + w] = meta.bin

      # random crop
      x2 = random.randint(0, max_w - target_width)
      y2 = random.randint(0, max_h - target_height)

      meta.bin = pad_img[y2: y2 + target_height, x2: x2 + target_width]

    elif isinstance(meta, T.BoxListMeta):
      assert meta.is_affine_size
      meta.bboxes += [x1, y1, x1, y1]
      meta.bboxes -= [x2, y2, x2, y2]
      meta.set_affine_size(max_h=target_height, max_w=target_width)
      meta.clip_with_affine_size()

  return metas


def random_crop_and_pad(inputs, target_height, target_width, fill_value=0, **kwargs):
  """random crop and padding image to target_height and target_width

    if image width or height is smaller than target size, it will prefer to pad
      to max side and then implement random crop.

    if image width or height is less than target size, it will random paste image
      to target size.

  Args:
      inputs ([type]): [description]
      target_height ([int]): target height
      target_width ([int]): target width
      fill_value ([float]): default to 0
  """
  if T.IsNumpy(inputs):
    raise NotImplementedError
  elif T.IsMeta(inputs):
    return _random_crop_and_pad_meta(inputs, target_height, target_width, fill_value, **kwargs)
  elif T.IsTensor(inputs):
    raise NotImplementedError
  elif T.IsPilImage(inputs):
    raise NotImplementedError


@T.MetaWrapper(support=[T.ImageMeta, T.BoxListMeta])
def _center_crop_and_pad_meta(metas, target_height, target_width, fill_value=0, **kwargs):
  """process one by one.
  """
  assert target_height > 0 and target_width > 0

  for meta in metas:

    if isinstance(meta, T.ImageMeta):
      assert meta.bin.ndim == 3, "current require input to be 3-channel."
      h, w, c = meta.bin.shape

      crop_x = max([0, (target_width - w) // 2])
      crop_y = max([0, (target_height - h) // 2])
      crop_w = min([target_width, w])
      crop_h = min([target_height, h])

      src_x = max([0, (w - target_width) // 2])
      src_y = max([0, (h - target_height) // 2])

      new_img = np.ones([target_height, target_width, c], dtype=meta.bin.dtype) * fill_value
      new_img[crop_y: crop_y + crop_h, crop_x: crop_x + crop_w] = meta.bin[src_y: src_y + crop_h, src_x: src_x + crop_w]

      meta.bin = new_img

    elif isinstance(meta, T.BoxListMeta):
      assert meta.is_affine_size
      meta.bboxes -= [src_x, src_y, src_x, src_y]
      meta.bboxes += [crop_x, crop_y, crop_x, crop_y]
      meta.set_affine_size(max_h=target_height, max_w=target_width)
      meta.clip_with_affine_size()

  return metas


def center_crop_and_pad(inputs, target_height, target_width, fill_value=0, **kwargs):
  """center crop and padding image to target_height and target_width

    if image width or height is smaller than target size, it will prefer to pad
      to max side and then implement center crop.

    if image width or height is less than target size, it will center paste image
      to target size.

  Args:
      inputs ([type]): [description]
      target_height ([int]): target height
      target_width ([int]): target width
      fill_value ([float]): default to 0
  """
  if T.IsNumpy(inputs):
    raise NotImplementedError
  elif T.IsMeta(inputs):
    return _center_crop_and_pad_meta(inputs, target_height, target_width, fill_value, **kwargs)
  elif T.IsTensor(inputs):
    raise NotImplementedError
  elif T.IsPilImage(inputs):
    raise NotImplementedError

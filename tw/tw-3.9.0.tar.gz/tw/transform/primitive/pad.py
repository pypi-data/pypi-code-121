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
"""PAD
"""
from typing import Sequence
import math
import random
import cv2
import numpy as np
import torch
from torch.nn import functional as F
import torchvision.transforms.functional as tvf
import torchvision.transforms as tvt
import kornia
import PIL

from tw import transform as T
from tw import logger


__all__ = [
    'pad',
    'pad_to_size_divisible',
    'pad_to_square',
    'random_expand',
]

#!<----------------------------------------------------------------------------
#!< PAD VALUE
#!<----------------------------------------------------------------------------


def _pad_np(inputs, left, top, right, bottom, fill_value=0):

  if inputs.ndim == 3:
    h, w, c = inputs.shape
  else:
    h, w = inputs.shape

  new_w = left + w + right
  new_h = top + h + bottom

  if inputs.ndim == 3:
    img = np.ones(shape=[new_h, new_w, c], dtype=inputs.dtype) * fill_value
    img[top:top + h, left:left + w, :] = inputs
  else:
    img = np.ones(shape=[new_h, new_w], dtype=inputs.dtype) * fill_value
    img[top:top + h, left:left + w] = inputs

  return img


@T.MetaWrapper(support=[T.ImageMeta, T.BoxListMeta, T.KpsListMeta])
def _pad_meta(metas: Sequence[T.MetaBase], left, top, right, bottom, fill_value=0):
  r"""pad space around sample.
  """
  for meta in metas:

    if isinstance(meta, T.ImageMeta):
      h, w, c = meta.bin.shape
      new_w = left + w + right
      new_h = top + h + bottom
      img = np.ones(shape=[new_h, new_w, c], dtype=meta.bin.dtype) * fill_value
      img[top:top + h, left:left + w, :] = meta.bin
      meta.bin = img

    if isinstance(meta, T.BoxListMeta):
      assert meta.is_affine_size
      meta.bboxes += [left, top, left, top]
      width = meta.max_x + left + right
      height = meta.max_y + top + bottom
      meta.set_affine_size(height, width)
      meta.clip_with_affine_size()

    if isinstance(meta, T.KpsListMeta):
      assert meta.is_affine_size
      meta.keypoints += [left, top]
      width = meta.max_x + left + right
      height = meta.max_y + top + bottom
      meta.set_affine_size(height, width)
      meta.clip_with_affine_size()

  return metas


def pad(inputs, left, top, right, bottom, fill_value=0):
  if T.IsNumpy(inputs):
    raise _pad_np(inputs, left, top, right, bottom, fill_value=fill_value)
  elif T.IsMeta(inputs):
    return _pad_meta(inputs, left, top, right, bottom, fill_value=fill_value)
  elif T.IsTensor(inputs):
    return F.pad(inputs, [left, right, top, bottom], mode='constant', value=fill_value)
  elif T.IsPilImage(inputs):
    return tvt.Pad((left, top, right, bottom), fill=fill_value)(inputs)


#!<----------------------------------------------------------------------------
#!< PAD TO SIZE DIVISIBLE
#!<----------------------------------------------------------------------------

def _pad_to_size_divisible_np(image_list: Sequence[np.ndarray], size_divisible=32):
  max_size = list(max(s) for s in zip(*[img.shape for img in image_list]))
  max_size[1] = int(math.ceil(max_size[1] / size_divisible) * size_divisible)
  max_size[2] = int(math.ceil(max_size[2] / size_divisible) * size_divisible)
  max_size = tuple(max_size)
  batch_shape = (len(image_list),) + max_size
  batched_imgs = image_list[0].new(*batch_shape).zero_()
  for img, pad_img in zip(image_list, batched_imgs):
    pad_img[: img.shape[0], : img.shape[1], : img.shape[2]].copy_(img)
  return batched_imgs


def _pad_to_size_divisible_tensor(image_list: Sequence[torch.Tensor], size_divisible=32):
  max_size = list(max(s) for s in zip(*[img.shape for img in image_list]))
  max_size[-1] = int(math.ceil(max_size[-1] / size_divisible) * size_divisible)
  max_size[-2] = int(math.ceil(max_size[-2] / size_divisible) * size_divisible)
  max_size = tuple(max_size)
  batch_shape = (len(image_list),) + max_size
  batched_imgs = image_list[0].new(*batch_shape).zero_()
  for img, pad_img in zip(image_list, batched_imgs):
    c, h, w = img.shape
    pad_img[: c, : h, : w] = img
  return batched_imgs


def pad_to_size_divisible(input_list, size_divisible=32, **kwargs):
  """padding images in a batch to be divisible

    if input is nd.array [H, W, C] format
    if input is torch.Tensor [C, H, W] format

  Args:
      image_list list[nd.array]:
      size_divisible: padding to divisible image list

  Returns:
      [np.array]: image_list nd.array[N, C, H, W]
  """
  assert isinstance(input_list, (list, tuple))
  if isinstance(input_list[0], np.ndarray):
    return _pad_to_size_divisible_np(input_list, size_divisible=size_divisible)
  elif isinstance(input_list[0], torch.Tensor):
    return _pad_to_size_divisible_tensor(input_list, size_divisible=size_divisible)
  else:
    raise NotImplementedError

#!<----------------------------------------------------------------------------
#!< PAD TO TARGET SIZE
#!<----------------------------------------------------------------------------


@T.MetaWrapper(support=[T.ImageMeta, T.BoxListMeta, T.KpsListMeta])
def _pad_to_target_size_meta(metas: Sequence[T.MetaBase], target_height, target_width,
                             fill_value=0, mode='center', **kwargs):

  def _get_coord(h, w):
    if mode == 'center':
      x1 = int((target_width - w) / 2)
      x2 = x1 + w
      y1 = int((target_height - h) / 2)
      y2 = y1 + h
    else:
      raise NotImplemented(mode)
    return x1, y1, x2, y2

  for meta in metas:

    if isinstance(meta, T.ImageMeta):
      h, w, c = meta.bin.shape
      assert h <= target_height and w <= target_width, f'{h} vs {target_height} and {w} vs {target_width}'
      img = np.ones(shape=[target_height, target_width, c], dtype=meta.bin.dtype) * fill_value
      x1, y1, x2, y2 = _get_coord(h, w)
      img[y1: y2, x1: x2, :] = meta.bin
      meta.bin = img

    if isinstance(meta, T.BoxListMeta):
      assert meta.is_affine_size
      x1, y1, x2, y2 = _get_coord(meta.max_y, meta.max_x)
      meta.bboxes += np.array([x1, y1, x1, y1])
      meta.set_affine_size(target_height, target_width)
      # meta.clip_with_affine_size()

    if isinstance(meta, T.KpsListMeta):
      assert meta.is_affine_size
      x1, y1, x2, y2 = _get_coord(meta.max_y, meta.max_x)
      meta.keypoints += np.array([x1, y1])
      meta.set_affine_size(target_height, target_width)
      # meta.clip_with_affine_size()

  return metas


def pad_to_target_size(inputs, target_height, target_width, fill_value=0, mode='center', **kwargs):
  """pad input to target size in terms of different mode.

  Args:
      inputs ([type]): [description]
      target_height (int):
      target_width (int):
      fill_value (int, optional): [description]. Defaults to 0.
      mode (str): center, top-left, top-right, bottom-left, bottom-right

  Returns:
      [type]: [description]
  """
  if T.IsNumpy(inputs):
    raise NotImplementedError
  elif T.IsMeta(inputs):
    return _pad_to_target_size_meta(inputs, target_height, target_width, fill_value, mode, **kwargs)
  elif T.IsTensor(inputs):
    raise NotImplementedError
  elif T.IsPilImage(inputs):
    raise NotImplementedError

#!<----------------------------------------------------------------------------
#!< PAD TO SQUARE (384, 256) -> (384, 384)
#!<----------------------------------------------------------------------------


@T.MetaWrapper(support=[T.ImageMeta, T.BoxListMeta, T.KpsListMeta])
def _pad_to_square_meta(metas: Sequence[T.MetaBase], fill_value=0):

  for meta in metas:

    if isinstance(meta, T.ImageMeta):
      h, w, c = meta.bin.shape
      long_side = max(w, h)
      img = np.ones(shape=[long_side, long_side, c], dtype=meta.bin.dtype) * fill_value
      img[0: h, 0: w, :] = meta.bin
      meta.bin = img

    if isinstance(meta, T.BoxListMeta):
      assert meta.is_affine_size
      long_side = max(meta.max_x, meta.max_y)
      meta.set_affine_size(long_side, long_side)
      # meta.clip_with_affine_size()

    if isinstance(meta, T.KpsListMeta):
      assert meta.is_affine_size
      long_side = max(meta.max_x, meta.max_y)
      meta.set_affine_size(long_side, long_side)
      # meta.clip_with_affine_size()

  return metas


def pad_to_square(inputs, fill_value=0, **kwargs):
  """pad input to square (old image located on left top of new image.)

  Args:
      inputs ([type]): [description]
      fill_value (int, optional): [description]. Defaults to 0.

  Returns:
      [type]: [description]
  """
  if T.IsNumpy(inputs):
    h, w = inputs.shape[:2]
    long_side = max(w, h)
    w_pad = w - long_side
    h_pad = h - long_side
    return _pad_np(inputs, 0, 0, w_pad, h_pad, fill_value=fill_value)
  elif T.IsMeta(inputs):
    return _pad_to_square_meta(inputs, fill_value=fill_value)
  elif T.IsTensor(inputs):
    h, w = inputs.shape[-2:]
    long_side = max(w, h)
    w_pad = w - long_side
    h_pad = h - long_side
    return F.pad(inputs, [0, w_pad, 0, h_pad], mode='constant', value=fill_value)
  elif T.IsPilImage(inputs):
    raise NotImplementedError

#!<----------------------------------------------------------------------------
#!< EXPAND
#!<----------------------------------------------------------------------------


def _random_expand_np(inputs, ratio_range, mean):
  """random expand inputs and paste on a random position."""
  ratio = random.uniform(ratio_range[0], ratio_range[1])

  if inputs.ndim == 3:
    h, w, c = inputs.shape
    shape = (int(h * ratio), int(w * ratio), c)
  else:
    h, w = inputs.shape
    shape = (int(h * ratio), int(w * ratio))

  if np.all(mean == mean[0]):
    expand_img = np.empty(shape, dtype=inputs.dtype)
    expand_img.fill(mean[0])
  else:
    expand_img = np.full(shape, mean, dtype=inputs.dtype)

  left = int(random.uniform(0, w * ratio - w))
  top = int(random.uniform(0, h * ratio - h))
  expand_img[top: top + h, left: left + w] = inputs

  return expand_img


@T.MetaWrapper(support=[T.ImageMeta, T.BoxListMeta, T.KpsListMeta])
def _random_expand_meta(metas: Sequence[T.MetaBase], ratio_range, mean, **kwargs):
  r"""pad space around sample.
  """
  ratio = random.uniform(ratio_range[0], ratio_range[1])

  for meta in metas:
    if isinstance(meta, T.ImageMeta):

      if meta.bin.ndim == 3:
        h, w, c = meta.bin.shape
        shape = (int(h * ratio), int(w * ratio), c)
      else:
        h, w = meta.bin.shape
        shape = (int(h * ratio), int(w * ratio))

      if np.all(mean == mean[0]):
        expand_img = np.empty(shape, dtype=meta.bin.dtype)
        expand_img.fill(mean[0])
      else:
        expand_img = np.full(shape, mean, dtype=meta.bin.dtype)

      left = int(random.uniform(0, w * ratio - w))
      top = int(random.uniform(0, h * ratio - h))
      expand_img[top: top + h, left: left + w] = meta.bin
      meta.bin = expand_img

  for meta in metas:

    if isinstance(meta, T.BoxListMeta):
      assert meta.is_affine_size
      if len(meta.bboxes) > 0:
        meta.bboxes += [left, top, left, top]
      meta.set_affine_size(meta.max_y * ratio, meta.max_x * ratio)
      meta.clip_with_affine_size()

    if isinstance(meta, T.KpsListMeta):
      assert meta.is_affine_size
      if len(meta.keypoints) > 0:
        meta.keypoints += [left, top]
      meta.set_affine_size(meta.max_y * ratio, meta.max_x * ratio)
      meta.clip_with_affine_size()

  return metas


def random_expand(inputs, ratio_range=(1, 4), mean=(0, 0, 0), **kwargs):
  """Random expand the image

    Randomly place the original image on a canvas of 'ratio' x original image
    size filled with mean values. The ratio is in the range of ratio_range.

  Args:
      inputs ([type]): [description]
      fill_value (int, optional): [description]. Defaults to 0.
      mean (tuple): mean value of dataset.
      ratio_range (tuple): range of expand ratio.

  Returns:
      [type]: [description]
  """
  if T.IsNumpy(inputs):
    return _random_expand_np(inputs, ratio_range, mean)
  elif T.IsMeta(inputs):
    return _random_expand_meta(inputs, ratio_range, mean, **kwargs)
  elif T.IsTensor(inputs):
    raise NotImplementedError
  elif T.IsPilImage(inputs):
    raise NotImplementedError

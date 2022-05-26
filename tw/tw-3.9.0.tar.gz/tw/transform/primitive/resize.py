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
"""RESIZE
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
#!< SHORTSIDE RESIZE
#!<----------------------------------------------------------------------------


def _get_shortside_shape(h, w, min_size):
  if (w <= h and w == min_size) or (h <= w and h == min_size):
    ow, oh = w, h
  # resize
  if w < h:
    ow = min_size
    oh = int(min_size * h / w)
  else:
    oh = min_size
    ow = int(min_size * w / h)
  return oh, ow


def _shortside_resize_np(inputs, min_size=256, interpolation=cv2.INTER_LINEAR):
  h, w = inputs.shape[:2]
  oh, ow = _get_shortside_shape(h, w, min_size)
  return cv2.resize(inputs, dsize=(ow, oh), interpolation=interpolation)


@T.MetaWrapper(support=[T.ImageMeta, T.VideoMeta, T.BoxListMeta, T.KpsListMeta])
def _shortside_resize_meta(metas: Sequence[T.MetaBase], min_size=256, interpolation=cv2.INTER_LINEAR, **kwargs):

  for meta in metas:
    if meta.source == T.COLORSPACE.HEATMAP:
      interpolation = cv2.INTER_NEAREST

    if isinstance(meta, T.ImageMeta):
      h, w = meta.bin.shape[:2]
      oh, ow = _get_shortside_shape(h, w, min_size)
      meta.bin = cv2.resize(meta.bin, dsize=(ow, oh), interpolation=interpolation)

    if isinstance(meta, T.VideoMeta):
      h, w = meta.bin.shape[1:3]
      oh, ow = _get_shortside_shape(h, w, min_size)
      meta.bin = np.array([cv2.resize(meta.bin[i], dsize=(ow, oh), interpolation=interpolation)
                           for i in range(meta.n)])

    if isinstance(meta, T.BoxListMeta):
      assert meta.is_affine_size
      oh, ow = _get_shortside_shape(meta.max_y, meta.max_x, min_size)
      scale_w = float(ow) / meta.max_x
      scale_h = float(oh) / meta.max_y
      meta.bboxes *= [scale_w, scale_h, scale_w, scale_h]
      meta.set_affine_size(oh, ow)

    if isinstance(meta, T.KpsListMeta):
      assert meta.is_affine_size
      oh, ow = _get_shortside_shape(meta.max_y, meta.max_x, min_size)
      scale_w = float(ow) / meta.max_x
      scale_h = float(oh) / meta.max_y
      meta.keypoints *= [scale_w, scale_h]
      meta.set_affine_size(oh, ow)

  return metas


def shortside_resize(inputs, min_size=256, interpolation=cv2.INTER_LINEAR, **kwargs):
  """inputs will be aspect sized by short side to min_size.

  Args:
      inputs ([type]): [description]
      min_size (int): image will aspect resize according to short side size.
      interpolation ([type], optional): [description]. Defaults to cv2.INTER_LINEAR.

  Returns:
      [type]: [description]
  """
  if T.IsNumpy(inputs):
    return _shortside_resize_np(inputs, min_size, interpolation)
  elif T.IsMeta(inputs):
    return _shortside_resize_meta(inputs, min_size, interpolation, **kwargs)
  elif T.IsTensor(inputs):
    raise NotImplementedError
  elif T.IsPilImage(inputs):
    return tvt.Resize(size=min_size, interpolation=T.INTER_CV_TO_PIL[interpolation])(inputs)

#!<----------------------------------------------------------------------------
#!< RESIZE
#!<----------------------------------------------------------------------------


def _resize_np(inputs, height, width, interpolation=cv2.INTER_LINEAR):
  return cv2.resize(inputs, dsize=(width, height), interpolation=interpolation)


@T.MetaWrapper(support=[T.ImageMeta, T.BoxListMeta, T.VideoMeta, T.KpsListMeta])
def _resize_meta(metas: Sequence[T.MetaBase], height, width, interpolation=cv2.INTER_LINEAR):

  for meta in metas:
    if meta.source == T.COLORSPACE.HEATMAP:
      interpolation = cv2.INTER_NEAREST

    if isinstance(meta, T.ImageMeta):
      h, w = meta.bin.shape[:2]
      meta.bin = cv2.resize(meta.bin, dsize=(width, height), interpolation=interpolation)
      meta.transform.append(('resize', h, height, w, width))

    if isinstance(meta, T.VideoMeta):
      h, w = meta.bin.shape[1:3]
      meta.bin = np.array([cv2.resize(meta.bin[i], dsize=(width, height), interpolation=interpolation)
                           for i in range(meta.n)])
      meta.transform.append(('resize', h, height, w, width))

    if isinstance(meta, T.BoxListMeta):
      assert meta.is_affine_size
      scale_w = float(width) / meta.max_x
      scale_h = float(height) / meta.max_y
      if len(meta.bboxes) > 0:
        meta.bboxes *= np.array([scale_w, scale_h, scale_w, scale_h])
      meta.transform.append(('resize', meta.max_y, height, meta.max_x, width))
      meta.set_affine_size(height, width)

    if isinstance(meta, T.KpsListMeta):
      assert meta.is_affine_size
      scale_w = float(width) / meta.max_x
      scale_h = float(height) / meta.max_y
      if len(meta.keypoints):
        meta.keypoints *= [scale_w, scale_h]
      meta.transform.append(('resize', meta.max_y, height, meta.max_x, width))
      meta.set_affine_size(height, width)

  return metas


@T.MetaWrapper(support=[T.ImageMeta, T.BoxListMeta, T.VideoMeta, T.KpsListMeta])
def _resize_scale_meta(metas: Sequence[T.MetaBase], scale_h, scale_w, interpolation=cv2.INTER_LINEAR):

  for meta in metas:
    if meta.source == T.COLORSPACE.HEATMAP:
      interpolation = cv2.INTER_NEAREST

    if isinstance(meta, T.ImageMeta):
      h, w = meta.bin.shape[:2]
      height, width = int(h * scale_h), int(w * scale_w)
      meta.bin = cv2.resize(meta.bin, dsize=(width, height), interpolation=interpolation)
      meta.transform.append(('resize_scale', scale_h, scale_w))

    if isinstance(meta, T.VideoMeta):
      h, w = meta.bin[0].shape[:2]
      height, width = int(h * scale_h), int(w * scale_w)
      meta.bin = np.array([cv2.resize(meta.bin[i], dsize=(width, height), interpolation=interpolation)
                           for i in range(meta.n)])
      meta.transform.append(('resize_scale', scale_h, scale_w))

    if isinstance(meta, T.BoxListMeta):
      assert meta.is_affine_size
      if len(meta.bboxes):
        meta.bboxes *= [scale_w, scale_h, scale_w, scale_h]
      meta.set_affine_size(height, width)
      meta.transform.append(('resize_scale', scale_h, scale_w))

    if isinstance(meta, T.KpsListMeta):
      assert meta.is_affine_size
      if len(meta.keypoints):
        meta.keypoints *= [scale_w, scale_h]
      meta.set_affine_size(height, width)
      meta.transform.append(('resize_scale', scale_h, scale_w))

  return metas


def resize(inputs, height, width, interpolation=cv2.INTER_LINEAR, **kwargs):
  if T.IsNumpy(inputs):
    return _resize_np(inputs, height, width, interpolation)
  elif T.IsMeta(inputs):
    return _resize_meta(inputs, height, width, interpolation, **kwargs)
  elif T.IsTensor(inputs):
    return kornia.resize(inputs, (height, width), mode=T.INTER_CV_TO_TCH[interpolation])
  elif T.IsPilImage(inputs):
    return tvt.functional.resize(inputs, size=(height, width), interpolation=T.INTER_CV_TO_PIL[interpolation])


def random_resize(inputs, scale_range=(1, 4), interpolation=cv2.INTER_LINEAR, **kwargs):
  """random resize inputs with aspect ratio.

  Args:
      inputs ([type]): [description]
      scale_range (tuple, optional): [description]. Defaults to (1, 4).
      interpolation ([type], optional): [description]. Defaults to cv2.INTER_LINEAR.

  Returns:
      [type]: [description]
  """
  _min, _max = scale_range
  scale = random.random() * (_max - _min) + _min

  if T.IsNumpy(inputs):
    h, w = inputs.shape[:2]
    return _resize_np(inputs, int(h * scale), int(w * scale), interpolation)
  elif T.IsMeta(inputs):
    return _resize_scale_meta(inputs, scale, scale, interpolation, **kwargs)
  elif T.IsTensor(inputs):
    raise NotImplementedError
  elif T.IsPilImage(inputs):
    raise NotImplementedError

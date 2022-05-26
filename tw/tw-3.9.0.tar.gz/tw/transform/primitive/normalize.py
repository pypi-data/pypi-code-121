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
"""NORMALIZE
"""
from typing import Sequence
import math
import random
import cv2
import numpy as np
from scipy.signal import convolve2d
import torch
import torchvision.transforms.functional as tvf
import torchvision.transforms as tvt
import kornia
import PIL

from tw import transform as T
from tw import logger


#!<----------------------------------------------------------------------------
#!< TO TENSOR
#!<----------------------------------------------------------------------------

def _to_tensor_np(inputs, scale=None, mean=None, std=None, **kwargs):

  if inputs.ndim == 3:
    m = torch.from_numpy(np.ascontiguousarray(inputs.transpose((2, 0, 1))))
  elif inputs.ndim == 2:
    m = torch.from_numpy(inputs)[None]
  else:
    raise NotImplementedError(inputs.ndim)

  m = m.type(torch.FloatTensor)
  if scale is not None:
    m = m.float().div(scale)
  if mean is not None:
    m.sub_(torch.tensor(mean)[:, None, None])
  if std is not None:
    m.div_(torch.tensor(std)[:, None, None])

  return m


def _to_tensor_pil(inputs, scale=None, mean=None, std=None, **kwargs):

  m = tvt.functional.pil_to_tensor(inputs)
  m = m.type(torch.FloatTensor)

  if scale is not None:
    m = m.float().div(scale)
  if mean is not None:
    m.sub_(mean[:, None, None])
  if std is not None:
    m.div_(std[:, None, None])

  return m


@T.MetaWrapper()
def _to_tensor_meta(metas: Sequence[T.MetaBase], scale=None, mean=None, std=None, **kwargs):
  mean = torch.tensor(mean) if mean is not None else None
  std = torch.tensor(std) if std is not None else None

  for meta in metas:

    if meta.source in [T.COLORSPACE.HEATMAP, T.COLORSPACE.FLOW]:
      meta.bin = torch.from_numpy(meta.bin)
      continue

    if isinstance(meta, T.ImageMeta):
      # for image
      if meta.bin.ndim == 3:
        m = torch.from_numpy(np.ascontiguousarray(meta.bin.transpose((2, 0, 1))))
      elif meta.bin.ndim == 2:
        m = torch.from_numpy(meta.bin)[None]
      elif meta.bin.ndim == 4:
        m = torch.from_numpy(np.ascontiguousarray(meta.bin.transpose((0, 3, 1, 2))))
      else:
        raise NotImplementedError(meta.bin.ndim)

      m = m.type(torch.FloatTensor)
      if scale is not None:
        m = m.float().div(scale)
      if mean is not None:
        m.sub_(mean[:, None, None])
      if std is not None:
        m.div_(std[:, None, None])
      meta.bin = m

    if isinstance(meta, T.VideoMeta):
      # for image
      if meta.bin.ndim == 4:
        m = torch.from_numpy(np.ascontiguousarray(meta.bin.transpose((3, 0, 1, 2))))
      else:
        raise NotImplementedError(meta.bin.ndim)

      m = m.type(torch.FloatTensor)
      if scale is not None:
        m = m.float().div(scale)
      if mean is not None:
        m.sub_(mean[:, None, None, None])
      if std is not None:
        m.div_(std[:, None, None, None])
      meta.bin = m

  return metas


def to_tensor(inputs, scale=None, mean=None, std=None, **kwargs):
  """to tensor: (x / scale - mean) / std and from HWC to CHW

  Args:
      inputs ([type]): [description]
      scale ([type], optional): [description]. Defaults to None.
      mean ([type], optional): [description]. Defaults to None.
      std ([type], optional): [description]. Defaults to None.

  Raises:
      NotImplementedError: [description]

  Returns:
      [type]: [description]
  """
  if T.IsNumpy(inputs):
    return _to_tensor_np(inputs, scale=scale, mean=mean, std=std)
  elif T.IsMeta(inputs):
    return _to_tensor_meta(inputs, scale=scale, mean=mean, std=std, **kwargs)
  elif T.IsTensor(inputs):
    raise NotImplementedError
  elif T.IsPilImage(inputs):
    return _to_tensor_pil(inputs, scale=scale, mean=mean, std=std)


#!<----------------------------------------------------------------------------
#!< TO TENSOR
#!<----------------------------------------------------------------------------

@T.MetaWrapper()
def _to_float_meta(metas: Sequence[T.MetaBase], **kwargs):
  for meta in metas:
    if isinstance(meta, T.ImageMeta):
      if meta.source in [T.COLORSPACE.HEATMAP, T.COLORSPACE.FLOW]:
        continue
      meta.bin = meta.bin.astype('float32')
  return metas


def to_float(inputs, **kwargs):
  """inputs format to float

  Args:
      inputs ([type]): [description]

  Raises:
      NotImplementedError: [description]

  Returns:
      [type]: [description]
  """
  if T.IsNumpy(inputs):
    return inputs.astype('float32')
  elif T.IsMeta(inputs):
    return _to_float_meta(inputs, **kwargs)
  elif T.IsTensor(inputs):
    return inputs.float()
  elif T.IsPilImage(inputs):
    raise NotImplementedError

#!<----------------------------------------------------------------------------
#!< EQUAL HIST
#!<----------------------------------------------------------------------------


def _equal_hist_np(inputs):

  x = inputs.astype('uint8')

  for c in range(x.shape[2]):
    img = x[..., c]
    histogram = cv2.calcHist([img], [0], None, [256], (0, 256)).ravel()
    h = [_f for _f in histogram if _f]
    if len(h) <= 1:
      return img.copy()
    step = np.sum(h[:-1]) // 255
    if not step:
      return img.copy()
    lut = np.empty(256, dtype=np.uint8)
    n = step // 2
    for i in range(256):
      lut[i] = min(n // step, 255)
      n += histogram[i]
    x[..., c] = cv2.LUT(img, np.array(lut))

  return x.astype(inputs.dtype)


@T.MetaWrapper(support=[T.ImageMeta])
def _equal_hist_meta(metas: Sequence[T.MetaBase], **kwargs):

  for meta in sample:

    if meta.source in [T.COLORSPACE.HEATMAP]:
      continue

    if isinstance(meta, T.ImageMeta):
      ori_type = meta.bin.dtype
      meta.bin = _equal_hist_np(meta.bin)

  return metas


def equal_hist(inputs, **kwargs):
  """Equalize the image histogram.

  Args:
      inputs ([type]): [description]

  Returns:
      [type]: [description]
  """
  if T.IsNumpy(inputs):
    return _equal_hist_np(inputs)
  elif T.IsMeta(inputs):
    return _equal_hist_meta(inputs, **kwargs)
  elif T.IsTensor(inputs):
    raise NotImplementedError
  elif T.IsPilImage(inputs):
    raise NotImplementedError

#!<----------------------------------------------------------------------------
#!< TRUNCATED STANDARDIZE
#!<----------------------------------------------------------------------------


def _truncated_standardize_np(inputs):

  if inputs.ndim == 3:
    h, w, c = inputs.shape
  elif inputs.ndim == 2:
    h, w = inputs.shape
    c = 1
  else:
    raise NotImplementedError(inputs.ndim)

  inputs = inputs.astype('float32')
  min_std = 1.0 / math.sqrt(float(h * w * c))
  adjust_std = max(np.std(inputs), min_std)

  return (inputs - np.mean(inputs)) / adjust_std


@T.MetaWrapper(support=[T.ImageMeta, T.VideoMeta])
def _truncated_standardize_meta(metas: Sequence[T.MetaBase], **kwargs):

  for meta in metas:

    if meta.source in [T.COLORSPACE.HEATMAP, T.COLORSPACE.FLOW]:
      continue

    if isinstance(meta, T.ImageMeta):
      meta.bin = _truncated_standardize_np(meta.bin)

    if isinstance(meta, T.VideoMeta):
      if meta.bin.ndim == 4:
        n, h, w, c = meta.bin.shape
      else:
        raise NotImplementedError(meta.bin.ndim)

      meta_bins = [_truncated_standardize_np(meta.bin[i]) for i in range(n)]
      meta.bin = np.array(meta_bins)

  return metas


def truncated_standardize(inputs, **kwargs):
  """truncated standardize from TensorFlow

  Args:
      inputs ([type]): [description]

  Returns:
      [type]: [description]
  """
  if T.IsNumpy(inputs):
    return _truncated_standardize_np(inputs)
  elif T.IsMeta(inputs):
    return _truncated_standardize_meta(inputs, **kwargs)
  elif T.IsTensor(inputs):
    raise NotImplementedError
  elif T.IsPilImage(inputs):
    raise NotImplementedError

#!<----------------------------------------------------------------------------
#!< LOCAL CONTRAST NORMALIZE
#!<----------------------------------------------------------------------------


def _local_contrast_normalize_np(inputs, p, q, c):
  assert inputs.ndim == 2, "require inputs shape is [h, w]"
  kernel = np.ones((p, q)) / (p * q)
  patch_mean = convolve2d(inputs, kernel, boundary='symm', mode='same')
  patch_sm = convolve2d(np.square(inputs), kernel, boundary='symm', mode='same')
  patch_std = np.sqrt(np.maximum(patch_sm - np.square(patch_mean), 0)) + c
  patch_ln = (inputs - patch_mean) / patch_std
  return patch_ln


@T.MetaWrapper(support=[T.ImageMeta])
def _local_contrast_normalize_meta(metas: Sequence[T.MetaBase], p=3, q=3, c=1, **kwargs):

  for meta in metas:

    if meta.source in [T.COLORSPACE.HEATMAP, T.COLORSPACE.FLOW]:
      continue

    if isinstance(meta, T.ImageMeta):
      meta.bin = _local_contrast_normalize_np(meta.bin, p, q, c)

  return metas


def local_contrast_normalize(inputs, p=3, q=3, c=1, **kwargs):
  """local contrast normalize

  Ref:
    "No-Reference Image Quality Assessment in the Spatial Domain"

  Note:
      a smaller normalization window size improves the performance. In practice
  we pick P = Q = 3 so the window size is much smaller than the input image patch.
  Note that with this local normalization each pixel may have a different local
  mean and variance.

  Args:
      inputs ([type]):
      p (int, optional):  the normalization window size.
      q (int, optional):  the normalization window size.
      c (int, optional):  C is a positive constant that prevents dividing by zero

  Returns:
      [type]: [description]
  """
  if T.IsNumpy(inputs):
    return _local_contrast_normalize_np(inputs, p, q, c, **kwargs)
  elif T.IsMeta(inputs):
    return _local_contrast_normalize_meta(inputs, p, q, c, **kwargs)
  elif T.IsTensor(inputs):
    raise NotImplementedError
  elif T.IsPilImage(inputs):
    raise NotImplementedError

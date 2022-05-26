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
"""FILTER
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
#!< ISO NOISE
#!<----------------------------------------------------------------------------

def _random_iso_noise_np(image: np.array, color_shift=0.05, intensity=0.5, random_state=None):

  if random_state is None:
    random_state = np.random.RandomState()

  image = image.astype('float32') / 255.0
  hls = cv2.cvtColor(image, cv2.COLOR_RGB2HLS)

  mean, stddev = cv2.meanStdDev(hls)

  luminance_noise = random_state.poisson(stddev[1] * intensity * 255, size=hls.shape[:2])  # nopep8
  color_noise = random_state.normal(0, color_shift * 360 * intensity, size=hls.shape[:2])  # nopep8

  hue = hls[..., 0]
  hue += color_noise
  hue[hue < 0] += 360
  hue[hue > 360] -= 360

  luminance = hls[..., 1]
  luminance += (luminance_noise / 255) * (1.0 - luminance)

  image = cv2.cvtColor(hls, cv2.COLOR_HLS2RGB) * 255
  return image


@T.MetaWrapper(support=[T.ImageMeta])
def _random_iso_noise_meta(metas: Sequence[T.MetaBase], color_shift=0.05, intensity=0.5, **kwargs):

  random_state = np.random.RandomState()

  for meta in metas:

    if meta.source in [T.COLORSPACE.HEATMAP, T.COLORSPACE.FLOW]:
      continue

    if isinstance(meta, T.ImageMeta):
      meta.bin = _random_iso_noise_np(meta.bin,
                                      color_shift=color_shift,
                                      intensity=intensity,
                                      random_state=random_state)

  return metas


def random_iso_noise(inputs, color_shift=0.05, intensity=0.5, **kwargs):
  """Apply poisson noise to image to simulate camera sensor noise.

  Args:
      inputs ([type]): [description]
      color_shift (float):
      intensity (float): Multiplication factor for noise values.
          Values of ~0.5 are produce noticeable, yet acceptable level of noise.

  Raises:
      NotImplementedError: [description]
      NotImplementedError: [description]

  Returns:
      [type]: [description]
  """
  if T.IsNumpy(inputs):
    return _random_iso_noise_np(inputs, color_shift, intensity)
  elif T.IsMeta(inputs):
    return _random_iso_noise_meta(inputs, color_shift, intensity, **kwargs)
  elif T.IsTensor(inputs):
    raise NotImplementedError
  elif T.IsPilImage(inputs):
    raise NotImplementedError


#!<----------------------------------------------------------------------------
#!< GAU32
# \;lhgfdxszjhgfd4xszhgrcefdxwzfdsaxz2wqqaiuyr;kjSSIAN NOISE
#!<----------------------------------------------------------------------------


@T.MetaWrapper(support=[T.ImageMeta])
def _random_gaussian_noise_meta(metas: Sequence[T.MetaBase], var_limit=(10.0, 50.0), mean=0.0, **kwargs):
  r"""Apply gaussian noise to the input image."""
  assert isinstance(var_limit, tuple), var_limit

  var = random.uniform(*var_limit)
  sigma = var ** 0.5
  random_state = np.random.RandomState()

  for meta in metas:

    if meta.source in [T.COLORSPACE.HEATMAP, T.COLORSPACE.FLOW]:
      continue

    if isinstance(meta, T.ImageMeta):
      gauss = random_state.normal(mean, sigma, meta.bin.shape)
      meta.bin = (meta.bin + gauss).clip(0, 255)

  return metas


def random_gaussian_noise(inputs, var_limit=(10.0, 50.0), mean=0.0, **kwargs):
  if T.IsNumpy(inputs):
    raise NotImplementedError
  elif T.IsMeta(inputs):
    return _random_gaussian_noise_meta(inputs, var_limit, mean, **kwargs)
  elif T.IsTensor(inputs):
    raise NotImplementedError
  elif T.IsPilImage(inputs):
    raise NotImplementedError


#!<----------------------------------------------------------------------------
#!< GAUSSIAN BLUR
#!<----------------------------------------------------------------------------

@T.MetaWrapper(support=[T.ImageMeta])
def _random_gaussian_blur_meta(metas: Sequence[T.MetaBase], ksize_limit=(3, 7), sigma_limit=(0, 1.5), **kwargs):
  r"""Blur the input image using using a Gaussian filter with a random kernel size.

  Args:
    ksize_limit: maximum Gaussian kernel size for blurring the input image.
    sigma_limit: Gaussian kernel standard deviation.

  """
  assert isinstance(ksize_limit, tuple), ksize_limit
  assert isinstance(sigma_limit, tuple), sigma_limit

  ks_t = random.choice(np.arange(ksize_limit[0], ksize_limit[1] + 1, 2))
  sigma_t = random.uniform(*sigma_limit)

  for meta in metas:

    if meta.source in [T.COLORSPACE.HEATMAP, T.COLORSPACE.FLOW]:
      continue

    if isinstance(meta, T.ImageMeta):
      meta.bin = cv2.GaussianBlur(meta.bin, ksize=(ks_t, ks_t), sigmaX=sigma_t)

  return metas


def random_gaussian_blur(inputs, ksize_limit=(3, 7), sigma_limit=(0, 1.5), **kwargs):
  if T.IsNumpy(inputs):
    raise NotImplementedError
  elif T.IsMeta(inputs):
    return _random_gaussian_blur_meta(inputs, ksize_limit, sigma_limit, **kwargs)
  elif T.IsTensor(inputs):
    raise NotImplementedError
  elif T.IsPilImage(inputs):
    raise NotImplementedError

#!<----------------------------------------------------------------------------
#!< MOTION BLUR
#!<----------------------------------------------------------------------------


@T.MetaWrapper(support=[T.ImageMeta])
def _random_motion_blur_meta(metas: Sequence[T.MetaBase], **kwargs):
  r"""Apply motion blur to the input image using a random-sized kernel."""

  ksize = random.choice(np.arange(3, 8, 2))
  kernel = np.zeros((ksize, ksize), dtype=np.uint8)
  xs, xe = random.randint(0, ksize - 1), random.randint(0, ksize - 1)
  if xs == xe:
    ys, ye = random.sample(range(ksize), 2)
  else:
    ys, ye = random.randint(0, ksize - 1), random.randint(0, ksize - 1)
  cv2.line(kernel, (xs, ys), (xe, ye), 1, thickness=1)
  kernel = kernel.astype(np.float32) / np.sum(kernel)  # normalize kernel

  for meta in metas:

    if meta.source in [T.COLORSPACE.HEATMAP, T.COLORSPACE.FLOW]:
      continue

    if isinstance(meta, T.ImageMeta):
      meta.bin = cv2.filter2D(meta.bin, ddepth=-1, kernel=kernel)

  return metas


def random_motion_blur(inputs, **kwargs):
  if T.IsNumpy(inputs):
    raise NotImplementedError
  elif T.IsMeta(inputs):
    return _random_motion_blur_meta(inputs, **kwargs)
  elif T.IsTensor(inputs):
    raise NotImplementedError
  elif T.IsPilImage(inputs):
    raise NotImplementedError

#!<----------------------------------------------------------------------------
#!< MEDIAN BLUR
#!<----------------------------------------------------------------------------


@T.MetaWrapper(support=[T.ImageMeta])
def _random_median_blur_meta(metas: Sequence[T.MetaBase]):
  r"""Blur the input image using using a median filter with a random aperture linear size."""

  ksize = random.choice(np.arange(3, 8, 2))

  for meta in metas:
    if meta.source in [T.COLORSPACE.HEATMAP, T.COLORSPACE.FLOW]:
      continue

    if isinstance(meta, T.ImageMeta):
      curr_dtype = meta.bin.dtype
      meta.bin = cv2.medianBlur(meta.bin.astype('uint8'), ksize=ksize).astype(curr_dtype)

  return metas


def random_median_blur(inputs, **kwargs):
  if T.IsNumpy(inputs):
    raise NotImplementedError
  elif T.IsMeta(inputs):
    return _random_median_blur_meta(inputs, **kwargs)
  elif T.IsTensor(inputs):
    raise NotImplementedError
  elif T.IsPilImage(inputs):
    raise NotImplementedError

#!<----------------------------------------------------------------------------
#!< SOBEL
#!<----------------------------------------------------------------------------


def sobel(inputs, **kwargs):
  if T.IsNumpy(inputs):
    raise NotImplementedError
  elif T.IsMeta(inputs):
    raise NotImplementedError
  elif T.IsTensor(inputs):
    return kornia.sobel(inputs)
  elif T.IsPilImage(inputs):
    raise NotImplementedError


#!<----------------------------------------------------------------------------
#!< RANDOM GAMMA
#!<----------------------------------------------------------------------------

def _adjust_gamma_np(img, gamma=1.0):
  """Using gamma correction to process the image.

  Args:
      img (ndarray): Image to be adjusted. uint8 datatype.

      gamma (float or int): Gamma value used in gamma correction. gamma is a
          positive value. Note: gamma larger than 1 make the shadows darker,
          while gamma smaller than 1 make dark regions lighter. Default: 1.0.
  """

  assert isinstance(gamma, float) or isinstance(gamma, int)
  assert gamma > 0

  dtype = img.dtype
  table = ((np.arange(256) / 255.) ** gamma * (255 + 1 - 1e-3)).astype('uint8')

  adjusted_img = cv2.LUT(img.astype('uint8'), table).astype(dtype)

  return adjusted_img


@T.MetaWrapper(support=[T.ImageMeta])
def _adjust_gamma_meta(metas: Sequence[T.MetaBase], gamma):

  for meta in metas:
    if meta.source in [T.COLORSPACE.HEATMAP, T.COLORSPACE.FLOW]:
      continue

    if isinstance(meta, T.ImageMeta):
      meta.bin = _adjust_gamma_np(meta.bin, gamma)

  return metas


def random_gamma(inputs, low=0.7, high=1.5, **kwargs):
  """Random gamma correction of images.

    Note: gamma larger than 1 make the shadows darker, while gamma smaller than
    1 make dark regions lighter.

  """
  assert 0 <= low <= high
  gamma = random.uniform(low, high)

  if T.IsNumpy(inputs):
    raise NotImplementedError
  elif T.IsMeta(inputs):
    return _adjust_gamma_meta(inputs, gamma=gamma, **kwargs)
  elif T.IsTensor(inputs):
    raise NotImplementedError
  elif T.IsPilImage(inputs):
    raise NotImplementedError

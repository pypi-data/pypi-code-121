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
"""COLORSPACE
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
#!< COLORSPACE TRANSFORM
#!<----------------------------------------------------------------------------


def _rgb_to_yuv_bt709_videorange_np(image: np.array, is_bgr=False):

  if is_bgr:
    B, G, R = np.split(image, 3, axis=2)
  else:
    R, G, B = np.split(image, 3, axis=2)

  Y = 0.1826 * R + 0.6142 * G + 0.0620 * B + 16  # [16, 235]
  U = -0.1007 * R - 0.3385 * G + 0.4392 * B + 128  # [16, 240]
  V = 0.4392 * R - 0.3990 * G - 0.0402 * B + 128  # [16, 240]

  yuv_image = np.concatenate([Y, U, V], axis=2)
  return yuv_image


def _rgb_to_yuv_bt709_videorange_tensor(image: torch.Tensor, is_bgr=False):

  if is_bgr:
    B, G, R = torch.split(image, 1, dim=-3)
  else:
    R, G, B = torch.split(image, 1, dim=-3)

  Y = 0.1826 * R + 0.6142 * G + 0.0620 * B + 16  # [16, 235]
  U = -0.1007 * R - 0.3385 * G + 0.4392 * B + 128  # [16, 240]
  V = 0.4392 * R - 0.3990 * G - 0.0402 * B + 128  # [16, 240]

  yuv_image = torch.cat([Y, U, V], dim=-3)
  return yuv_image


def _rgb_to_yuv_bt709_fullrange_np(image: np.array, is_bgr=False):

  if is_bgr:
    B, G, R = np.split(image, 3, axis=2)
  else:
    R, G, B = np.split(image, 3, axis=2)

  Y = 0.2126 * R + 0.7152 * G + 0.0722 * B  # [0, 255]
  U = -0.1146 * R - 0.3854 * G + 0.5000 * B + 128  # [0, 255]
  V = 0.5000 * R - 0.4542 * G - 0.0468 * B + 128  # [0, 255]

  yuv_image = np.concatenate([Y, U, V], axis=2)
  return yuv_image


def _rgb_to_yuv_bt709_fullrange_tensor(image: torch.Tensor, is_bgr=False):

  if is_bgr:
    B, G, R = torch.split(image, 1, dim=-3)
  else:
    R, G, B = torch.split(image, 1, dim=-3)

  Y = 0.2126 * R + 0.7152 * G + 0.0722 * B  # [0, 255]
  U = -0.1146 * R - 0.3854 * G + 0.5000 * B + 128  # [0, 255]
  V = 0.5000 * R - 0.4542 * G - 0.0468 * B + 128  # [0, 255]

  yuv_image = torch.cat([Y, U, V], dim=-3)
  return yuv_image


def _yuv_bt709_videorange_to_rgb_np(image: np.array, is_bgr=False):

  Y, U, V = np.split(image, 3, axis=2)

  Y = Y - 16
  U = U - 128
  V = V - 128

  R = 1.1644 * Y + 1.7927 * V
  G = 1.1644 * Y - 0.2132 * U - 0.5329 * V
  B = 1.1644 * Y + 2.1124 * U

  if is_bgr:
    return np.concatenate([B, G, R], axis=2)
  else:
    return np.concatenate([R, G, B], axis=2)


def _yuv_bt709_videorange_to_rgb_tensor(image: torch.Tensor, is_bgr=False):

  Y, U, V = torch.split(image, 1, dim=-3)

  Y = Y - 16
  U = U - 128
  V = V - 128

  R = 1.1644 * Y + 1.7927 * V
  G = 1.1644 * Y - 0.2132 * U - 0.5329 * V
  B = 1.1644 * Y + 2.1124 * U

  if is_bgr:
    return torch.cat([B, G, R], dim=-3)
  else:
    return torch.cat([R, G, B], dim=-3)


def _yuv_bt709_fullrange_to_rgb_np(image: np.array, is_bgr=False):

  Y, U, V = np.split(image, 3, axis=2)

  Y = Y
  U = U - 128
  V = V - 128

  R = 1.000 * Y + 1.570 * V
  G = 1.000 * Y - 0.187 * U - 0.467 * V
  B = 1.000 * Y + 1.856 * U

  if is_bgr:
    return np.concatenate([B, G, R], axis=2)
  else:
    return np.concatenate([R, G, B], axis=2)


def _yuv_bt709_fullrange_to_rgb_tensor(image: torch.Tensor, is_bgr=False):

  Y, U, V = torch.split(image, 1, dim=-3)

  Y = Y
  U = U - 128
  V = V - 128

  R = 1.000 * Y + 1.570 * V
  G = 1.000 * Y - 0.187 * U - 0.467 * V
  B = 1.000 * Y + 1.856 * U

  if is_bgr:
    return torch.cat([B, G, R], dim=-3)
  else:
    return torch.cat([R, G, B], dim=-3)


def _change_colorspace_np(image: np.array, src: T.COLORSPACE, dst: T.COLORSPACE):

  assert isinstance(src, T.COLORSPACE)
  assert isinstance(dst, T.COLORSPACE)

  code = T.COLORSPACE_MAPPING[(src, dst)]

  if code == 'RGB_TO_YUV_BT709_FULLRANGE':
    return _rgb_to_yuv_bt709_fullrange_np(image, is_bgr=False)
  elif code == 'BGR_TO_YUV_BT709_FULLRANGE':
    return _rgb_to_yuv_bt709_fullrange_np(image, is_bgr=True)
  elif code == 'RGB_TO_YUV_BT709_VIDEORANGE':
    return _rgb_to_yuv_bt709_videorange_np(image, is_bgr=False)
  elif code == 'BGR_TO_YUV_BT709_VIDEORANGE':
    return _rgb_to_yuv_bt709_videorange_np(image, is_bgr=True)
  elif code == 'YUV_BT709_FULLRANGE_TO_RGB':
    return _yuv_bt709_fullrange_to_rgb_np(image, is_bgr=False)
  elif code == 'YUV_BT709_FULLRANGE_TO_BGR':
    return _yuv_bt709_fullrange_to_rgb_np(image, is_bgr=True)
  elif code == 'YUV_BT709_VIDEORANGE_TO_RGB':
    return _yuv_bt709_videorange_to_rgb_np(image, is_bgr=False)
  elif code == 'YUV_BT709_VIDEORANGE_TO_BGR':
    return _yuv_bt709_videorange_to_rgb_np(image, is_bgr=True)
  return cv2.cvtColor(image, code)


def _change_colorspace_tensor(image: np.array, src: T.COLORSPACE, dst: T.COLORSPACE):

  assert isinstance(src, T.COLORSPACE)
  assert isinstance(dst, T.COLORSPACE)

  code = T.COLORSPACE_MAPPING[(src, dst)]

  if code == 'RGB_TO_YUV_BT709_FULLRANGE':
    return _rgb_to_yuv_bt709_fullrange_tensor(image, is_bgr=False)
  elif code == 'BGR_TO_YUV_BT709_FULLRANGE':
    return _rgb_to_yuv_bt709_fullrange_tensor(image, is_bgr=True)
  elif code == 'RGB_TO_YUV_BT709_VIDEORANGE':
    return _rgb_to_yuv_bt709_videorange_tensor(image, is_bgr=False)
  elif code == 'BGR_TO_YUV_BT709_VIDEORANGE':
    return _rgb_to_yuv_bt709_videorange_tensor(image, is_bgr=True)
  elif code == 'YUV_BT709_FULLRANGE_TO_RGB':
    return _yuv_bt709_fullrange_to_rgb_tensor(image, is_bgr=False)
  elif code == 'YUV_BT709_FULLRANGE_TO_BGR':
    return _yuv_bt709_fullrange_to_rgb_tensor(image, is_bgr=True)
  elif code == 'YUV_BT709_VIDEORANGE_TO_RGB':
    return _yuv_bt709_videorange_to_rgb_tensor(image, is_bgr=False)
  elif code == 'YUV_BT709_VIDEORANGE_TO_BGR':
    return _yuv_bt709_videorange_to_rgb_tensor(image, is_bgr=True)
  elif code == cv2.COLOR_BGR2RGB:
    b, g, r = torch.split(image, 1, dim=-3)
    return torch.cat([r, g, b], dim=-3)
  elif code == cv2.COLOR_RGB2BGR:
    r, g, b = torch.split(image, 1, dim=-3)
    return torch.cat([b, g, r], dim=-3)
  else:
    raise NotADirectoryError(code)


@T.MetaWrapper(support=[T.ImageMeta, T.VideoMeta, T.BoxListMeta, T.KpsListMeta])
def _change_colorspace_meta(metas: Sequence[T.MetaBase], src: T.COLORSPACE, dst: T.COLORSPACE, **kwargs):

  for meta in metas:

    if meta.source in [T.COLORSPACE.HEATMAP, T.COLORSPACE.FLOW]:
      continue

    if isinstance(meta, T.ImageMeta):
      meta.bin = _change_colorspace_np(meta.bin, src, dst)
      meta.source = dst

    if isinstance(meta, T.VideoMeta):
      for i in range(meta.n):
        meta.bin[i] = _change_colorspace_np(meta.bin[i], src, dst)

  return metas


def change_colorspace(inputs, src: T.COLORSPACE, dst: T.COLORSPACE, **kwargs):
  """inputs will be aspect sized by short side to min_size.

  Args:
      inputs ([type]): [description]
      min_size (int): image will aspect resize according to short side size.
      interpolation ([type], optional): [description]. Defaults to cv2.INTER_LINEAR.

  Returns:
      [type]: [description]
  """
  if T.IsNumpy(inputs):
    return _change_colorspace_np(inputs, src, dst)
  elif T.IsMeta(inputs):
    return _change_colorspace_meta(inputs, src, dst, **kwargs)
  elif T.IsTensor(inputs):
    return _change_colorspace_tensor(inputs, src, dst)
  elif T.IsPilImage(inputs):
    raise NotImplementedError

#!<----------------------------------------------------------------------------
#!< PHOTOMETRIC DISTORTION
#!<----------------------------------------------------------------------------


def _random_photometric_distortion_numpy(image,
                                         brightness_delta=32,
                                         contrast_range=(0.5, 1.5),
                                         saturation_range=(0.5, 1.5),
                                         hue_delta=18):
  # random brightness
  if random.randint(0, 2):
    delta = random.uniform(-brightness_delta, brightness_delta)
    image += delta

  # mode == 0 --> do random contrast first
  # mode == 1 --> do random contrast last
  mode = random.randint(0, 2)
  if mode == 1:
    if random.randint(0, 2):
      alpha = random.uniform(contrast_range[0], contrast_range[1])
      image *= alpha

  # convert color from BGR to HSV
  image = change_colorspace(image, src=T.COLORSPACE.BGR, dst=T.COLORSPACE.HSV)

  # random saturation
  if random.randint(0, 2):
    image[..., 1] *= random.uniform(saturation_range[0], saturation_range[1])

  # random hue
  if random.randint(0, 2):
    image[..., 0] += random.uniform(-hue_delta, hue_delta)
    image[..., 0][image[..., 0] > 360] -= 360
    image[..., 0][image[..., 0] < 0] += 360

  # convert color from HSV to BGR
  image = change_colorspace(image, src=T.COLORSPACE.HSV, dst=T.COLORSPACE.BGR)

  # random contrast
  if mode == 0:
    if random.randint(0, 2):
      alpha = random.uniform(contrast_range[0], contrast_range[1])
      image *= alpha

  # randomly swap channels
  # if random.randint(0, 2):
  #   axis = [0, 1, 2]
  #   random.shuffle(axis)
  #   image = image[..., axis]

  return image


@T.MetaWrapper(support=[T.ImageMeta, T.VideoMeta, T.BoxListMeta, T.KpsListMeta])
def _random_photometric_distortion_meta(metas: Sequence[T.MetaBase],
                                        brightness_delta=32,
                                        contrast_range=(0.5, 1.5),
                                        saturation_range=(0.5, 1.5),
                                        hue_delta=18,
                                        **kwargs):
  """NOTE: different augmentation in batch of ImageMeta.
  """
  seed = random.randint(0, 2**32-1)

  for meta in metas:
    # all meta with same augmentation
    random.seed(seed)

    if meta.source in [T.COLORSPACE.HEATMAP]:
      continue

    if isinstance(meta, T.ImageMeta):
      meta.bin = _random_photometric_distortion_numpy(meta.bin,
                                                      brightness_delta,
                                                      contrast_range,
                                                      saturation_range,
                                                      hue_delta)

    if isinstance(meta, T.VideoMeta):
      # it should support 4-channel operation
      meta.bin = _random_photometric_distortion_numpy(meta.bin,
                                                      brightness_delta,
                                                      contrast_range,
                                                      saturation_range,
                                                      hue_delta)

  return metas


def random_photometric_distortion(inputs,
                                  brightness_delta=32,
                                  contrast_range=(0.5, 1.5),
                                  saturation_range=(0.5, 1.5),
                                  hue_delta=18,
                                  **kwargs):
  """Apply photometric distortion to image sequentially, every transformation
    is applied with a probability of 0.5. The position of random contrast is in
    second or second to last.

    1. random brightness
    2. random contrast (mode 0)
    3. convert color from BGR to HSV
    4. random saturation
    5. random hue
    6. convert color from HSV to BGR
    7. random contrast (mode 1)
    # 8. randomly swap channels

  Args:
      brightness_delta (int): delta of brightness.
      contrast_range (tuple): range of contrast.
      saturation_range (tuple): range of saturation.
      hue_delta (int): delta of hue.
  """
  if T.IsNumpy(inputs):
    return _random_photometric_distortion_numpy(inputs, brightness_delta, contrast_range, saturation_range, hue_delta)
  elif T.IsMeta(inputs):
    return _random_photometric_distortion_meta(
        inputs, brightness_delta, contrast_range, saturation_range, hue_delta, **kwargs)
  elif T.IsTensor(inputs):
    raise NotImplementedError
  elif T.IsPilImage(inputs):
    raise NotImplementedError

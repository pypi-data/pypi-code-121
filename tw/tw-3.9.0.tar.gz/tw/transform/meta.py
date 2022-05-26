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
import os
import sys
import functools
from enum import Enum

import torch
import numpy as np
import cv2
import PIL

from tw import logger
from tw import fs
from tw.media import raw

#!<-----------------------------------------------------------------------------
#!< Constant
#!<-----------------------------------------------------------------------------


class COLORSPACE(Enum):
  RGB = 0
  BGR = 1
  BGRA = 2
  RBGA = 3
  HLS = 4
  HSV = 5
  HEATMAP = 10
  GRAY = 11
  FEATURE = 12
  FLOW = 13
  BT709_FULLRANGE = 20
  BT601_FULLRANGE = 21
  BT709_VIDEORANGE = 22
  BT601_VIDEORANGE = 23
  BAYER = 31
  XTRANS = 32


#!<-----------------------------------------------------------------------------
#!< MetaBase
#!<-----------------------------------------------------------------------------

class MetaBase():
  def __init__(self, name='MetaBase'):
    self.name = name
    self.source = None
    self.path = None
    self.bin = None

  def numpy(self):
    return self

  def to(self, device):
    return self

  def __str__(self):
    return 'MetaBase'

  def __len__(self):
    return 0


#!<-----------------------------------------------------------------------------
#!< Waveform Meta
#!<-----------------------------------------------------------------------------

class WaveformMeta(MetaBase):
  def __init__(self, name='WaveformMeta'):
    super(WaveformMeta, self).__init__(name)

  def __str__(self):
    s = '  WaveformMeta=> {}\n'.format(self.name)
    return s

#!<-----------------------------------------------------------------------------
#!< Video Meta: sequential images
#!<-----------------------------------------------------------------------------


class VideoMeta(MetaBase):
  r"""VideoMeta: a list of images with same size.

  Args:
    name (string/int): the identifier
    source (string): 'image' for normal rgb, 'mask' for heatmap.
    path (list of string): a list of images
    binary (a numpy file): [frame, h, w, c]

  """

  def __init__(self, name='VideoMeta', source=COLORSPACE.BGR, path=None, binary=None):
    super(VideoMeta, self).__init__(name)
    self.source = source

    # path
    if path is not None:
      assert isinstance(path, list), "path should be a image path list."
      for p in path:
        fs.raise_path_not_exist(path)
    self.path = path

    # attribute
    self.bin = binary
    if self.bin is None:
      self.h = 0
      self.w = 0
      self.c = 0
      self.n = 0
    else:
      self.numpy()
      self.n, self.h, self.w, self.c = self.bin.shape

    # labels
    self.label = []
    self.caption = []
    self.transform = []   # transform op

  def __str__(self):
    s = '  VideoMeta=> {}\n'.format(self.name)
    s += '    source: {}\n'.format(self.source)
    s += '    path: {}\n'.format(self.path)
    s += '    shape: (h={}, w={}, c={})\n'.format(self.h, self.w, self.c)

    if self.bin is not None:
      if len(self.bin.shape) == 4:
        n, h, w, c = self.bin.shape
      else:
        raise NotImplementedError(self.bin.shape)

      s += '    binary: (n={}, h={}, w={}, c={}, type={})\n'.format(
          n, h, w, c, self.bin.__class__.__name__)
      s += '    numerical: (max={}, min={}, avg={})\n'.format(
          self.bin.max(), self.bin.min(), self.bin.mean())
    if self.label:
      s += '    label: {}\n'.format(self.label)
    if self.caption:
      s += '    captions: {}\n'.format(self.caption)
    if self.transform is not None:
      s += '    transform: {}\n'.format(self.transform)
    return s

  def numpy(self):
    if self.source == COLORSPACE.HEATMAP:
      self.bin = np.array(self.bin).astype('uint8')
    else:
      self.bin = np.array(self.bin).astype('float32')
    return self

  def load(self):
    if self.bin is None:
      self.bin = np.array([cv2.imread(p, cv2.IMREAD_UNCHANGED) for p in self.path])  # nopep8
      if len(self.bin.shape) == 4:
        self.n, self.h, self.w, self.c = self.bin.shape
      else:
        raise NotImplementedError(self.bin.shape, self.path)
    return self

#!<-----------------------------------------------------------------------------
#!< Image Meta
#!<-----------------------------------------------------------------------------


class ImageMeta(MetaBase):
  """ImageMeta

  Args:
    name (string/int): the identifier
    source (string): 'image' for normal rgb, 'mask' for heatmap.
    path (string): path to source
    binary: binary format like nd.array

  """

  def __init__(self, name='ImageMeta', source=COLORSPACE.BGR, path=None, binary=None):
    super(ImageMeta, self).__init__(name)
    self.source = source

    if path is not None:
      fs.raise_path_not_exist(path)

    self.path = path  # path to image
    self.bin = binary   # raw inputs format

    self.label = []
    self.caption = []
    self.transform = []   # transform op

  @property
  def h(self):
    return self.bin.shape[0]

  @property
  def w(self):
    return self.bin.shape[1]

  @property
  def c(self):
    if self.bin.ndim == 3:
      return self.bin.shape[2]
    elif self.bin.ndim == 2:
      return 1
    else:
      return -1

  def __str__(self):
    s = '  ImageMeta => {}\n'.format(self.name)
    s += '    source: {}\n'.format(self.source)
    s += '    path: {}\n'.format(self.path)
    s += '    shape: (h={}, w={}, c={})\n'.format(self.h, self.w, self.c)
    if self.bin is not None:
      s += '    binary: (h={}, w={}, c={}, type={})\n'.format(self.h, self.w, self.c, self.bin.__class__.__name__)
      s += '    numerical: (max={}, min={}, avg={})\n'.format(self.bin.max(), self.bin.min(), self.bin.mean())
    if self.label:
      s += '    label: {}\n'.format(self.label)
    if self.caption:
      s += '    captions: {}\n'.format(self.caption)
    if self.transform is not None:
      s += '    transform: {}\n'.format(self.transform)
    return s

  def numpy(self):
    if self.source in [COLORSPACE.HEATMAP, ]:
      self.bin = np.array(self.bin).astype('uint8')
    else:
      self.bin = np.array(self.bin).astype('float32')
    return self

  def load(self):
    # if binary file has existed, return self
    if self.bin is not None:
      return self

    # loading file in terms of their extension
    if os.path.splitext(os.path.basename(self.path))[1].upper() in ['.CR2', '.NEF', '.ARW']:
      self.bin = raw.read_raw(self.path)
      self.c, self.h, self.w = self.bin.shape
    else:
      self.bin = cv2.imread(self.path, cv2.IMREAD_UNCHANGED)

    return self

#!<-----------------------------------------------------------------------------
#!< BoxList Meta
#!<-----------------------------------------------------------------------------


class BoxListMeta(MetaBase):
  def __init__(self, name='BoxListMeta'):
    super(BoxListMeta, self).__init__(name)
    self.format = 'xyxy'
    self.bboxes = []
    self.bboxes_count = 0
    self.label = []
    self.caption = []
    self.transform = []
    self.extra = []

    # affine to image size
    self.max_x = sys.float_info.max
    self.min_x = -sys.float_info.max
    self.max_y = sys.float_info.max
    self.min_y = -sys.float_info.max
    self.is_affine_size = False
    self.visibility = True
    self.min_area = 0.0

  def set_affine_size(self, max_h, max_w, min_area=0.0, visibility=True):
    self.min_area = min_area
    self.visibility = visibility
    self.is_affine_size = True
    self.min_x, self.max_x, self.min_y, self.max_y = 0, max_w - 1, 0, max_h - 1
    return self

  def clip_with_affine_size(self):
    assert isinstance(self.bboxes, np.ndarray)
    self.bboxes = self.bboxes.clip(
        [self.min_x, self.min_y, self.min_x, self.min_y],
        [self.max_x, self.max_y, self.max_x, self.max_y])
    return self

  def numpy(self):
    self.bboxes = np.array(self.bboxes).astype('float32')
    return self

  def __str__(self):
    s = '  BoxListMeta => {}\n'.format(self.name)
    total = []
    if self.bboxes_count:
      total.append(self.bboxes)
    if self.label is not None:
      total.append(self.label)
    if len(self.caption):
      total.append(self.caption)
    if len(self.extra) != 0:
      for key in self.extra:
        total.append(getattr(self, key))
    for i, item in enumerate(zip(*total)):
      s += '    {}: {}\n'.format(i, item)
    if self.transform is not None:
      s += '    transform: {}\n'.format(self.transform)
    return s

  def add(self, x1, y1, x2, y2, label=None, caption=None, **kwargs):
    self.bboxes.append([x1, y1, x2, y2])
    self.bboxes_count += 1
    if label is not None:
      self.label.append(label)
    if caption is not None:
      self.caption.append(caption)
    for key, value in kwargs.items():
      if hasattr(self, key):
        getattr(self, key).append(value)
      else:
        setattr(self, key, [value, ])
        self.extra.append(key)

    return self

#!<-----------------------------------------------------------------------------
#!< Keypoints Meta
#!<-----------------------------------------------------------------------------


class KpsListMeta(MetaBase):
  def __init__(self, name='KpsListMeta'):
    super(KpsListMeta, self).__init__(name)
    self.format = 'xy'
    self.keypoints = []
    self.keypoints_count = 0
    self.label = []
    self.caption = []
    self.transform = []

    # affine to image size
    self.max_x = sys.float_info.max
    self.min_x = -sys.float_info.max
    self.max_y = sys.float_info.max
    self.min_y = -sys.float_info.max
    self.is_affine_size = False
    self.visibility = True

  def set_affine_size(self, max_h, max_w, visibility=True):
    self.visibility = visibility
    self.is_affine_size = True
    self.min_x, self.max_x, self.min_y, self.max_y = 0, max_w, 0, max_h
    return self

  def clip_with_affine_size(self):
    assert isinstance(self.keypoints, np.ndarray)
    self.keypoints = self.keypoints.clip(
        [self.min_x, self.min_y], [self.max_x, self.max_y])
    return self

  def __str__(self):
    s = '  KpsMeta=> {}\n'.format(self.name)
    total = []
    if self.keypoints_count:
      total.append(self.keypoints)
    if self.label is not None:
      total.append(self.label)
    if self.caption is not None:
      total.append(self.caption)
    for i, item in enumerate(zip(*total)):
      s += '    {}: {}\n'.format(i, item)
    if self.transform is not None:
      s += '    transform: {}\n'.format(self.transform)
    return s

  def numpy(self):
    self.keypoints = np.array(self.keypoints).astype('float32')
    return self

  def add(self, x, y, label=None, caption=None):
    self.keypoints.append([x, y])
    self.keypoints_count += 1
    if label is not None:
      self.label.append(label)
    if caption is not None:
      self.caption.append(caption)
    return self

#!<-----------------------------------------------------------------------------
#!< Point Cloud Meta
#!<-----------------------------------------------------------------------------


class PointCloudMeta(MetaBase):
  def __init__(self, name='PointCloudMeta'):
    super(PointCloudMeta, self).__init__(name)
    self.format = 'xyz'

    self.points = []  # [k, xyz]
    self.colors = []  # [k, rgb] photometric device
    self.labels = []  # [k,]
    self.index = []  # [k,]
    self.cloud = -1  # cloud index

    # self.transform = None

    # # affine to image size
    # self.max_x = sys.float_info.max
    # self.min_x = -sys.float_info.max
    # self.max_y = sys.float_info.max
    # self.min_y = -sys.float_info.max
    # self.is_affine_size = False
    # self.visibility = True

  # def set_affine_size(self, max_h, max_w, visibility=True):
  #   self.visibility = visibility
  #   self.is_affine_size = True
  #   self.min_x, self.max_x, self.min_y, self.max_y = 0, max_w, 0, max_h
  #   return self

  # def clip_with_affine_size(self):
  #   assert isinstance(self.keypoints, np.ndarray)
  #   self.keypoints = self.keypoints.clip(
  #       [self.min_x, self.min_y], [self.max_x, self.max_y])
  #   return self

  # def __str__(self):
  #   s = '  KpsMeta=> {}\n'.format(self.name)
  #   total = []
  #   if self.keypoints_count:
  #     total.append(self.keypoints)
  #   if self.label is not None:
  #     total.append(self.label)
  #   if self.caption is not None:
  #     total.append(self.caption)
  #   for i, item in enumerate(zip(*total)):
  #     s += '    {}: {}\n'.format(i, item)
  #   if self.transform is not None:
  #     s += '    transform: {}\n'.format(self.transform)
  #   return s

  # def numpy(self):
  #   self.keypoints = np.array(self.keypoints).astype('float32')
  #   return self

  # def add(self, x, y, label=None, caption=None):
  #   self.keypoints.append([x, y])
  #   self.keypoints_count += 1
  #   if label is not None:
  #     self.label.append(label)
  #   if caption is not None:
  #     self.caption.append(caption)
  #   return self

#!<-----------------------------------------------------------------------------
#!< Utils
#!<-----------------------------------------------------------------------------


def MetaWrapper(support=[], **kwargs):
  r"""Decorator for supplying meta actions. It functions as:

    1. convert single meta into list of metas
    2. select user-specific meta index to augment
    3. checking if current augment to allow meta type pass.

  """
  def wrapper(transform):
    @functools.wraps(transform)
    def kernel(inputs, *args, **kwargs):
      # convert to list
      if not isinstance(inputs, list):
        inputs = [inputs]
      # check select
      if 'select' in kwargs:
        selects = []
        for i in kwargs['select']:
          selects.append(inputs[i])
        inputs = selects
      # check allowing
      if len(support) > 0:
        for inp in inputs:
          if type(inp) not in support:
            logger.error('Failed to find {} in {} on {}'.format(type(inp), support, transform))
      return transform(inputs, *args, **kwargs)
    return kernel
  return wrapper


#!<-----------------------------------------------------------------------------
#!< Condition Checking
#!<-----------------------------------------------------------------------------

def IsNumpy(inputs):
  """If inputs is a numpy-like image with (h, w, c) format

  Args:
      inputs ([np.array]): [description]

  Returns:
      [bool]: [description]
  """

  if not isinstance(inputs, np.ndarray):
    return False

  assert inputs.ndim in [2, 3], f"{inputs.ndim}"

  if inputs.ndim == 3:
    assert inputs.shape[2] in [1, 3, 4], f"{inputs.shape}"

  return True


def IsTensor(inputs):
  """If inputs is a tensor image with (n, c, h, w) / (c, h, w) format

  Args:
      inputs ([torch.Tensor]): [description]

  Returns:
      [bool]: [description]
  """

  if not isinstance(inputs, torch.Tensor):
    return False

  assert inputs.ndim in [2, 3, 4], f"{inputs.ndim}"

  if inputs.ndim == 3:
    assert inputs.shape[0] in [1, 3, 4], f"{inputs.shape}"

  if inputs.ndim == 4:
    assert inputs.shape[1] in [1, 3, 4], f"{inputs.shape}"

  return True


def IsPilImage(inputs):
  """If inputs is a pil image.

  Args:
      inputs ([PIL.Image]): [description]

  Returns:
      [bool]: [description]
  """

  if not isinstance(inputs, PIL.Image.Image):
    return False

  return True


def IsMeta(inputs):
  """If inputs is a sample meta like.

  Args:
      inputs ([type]): [description]

  Returns:
      [type]: [description]
  """

  if not isinstance(inputs, (list, tuple, MetaBase)):
    return False

  return True

#!<-----------------------------------------------------------------------------
#!< Constant
#!<-----------------------------------------------------------------------------


INTER_CV_TO_PIL = {
    cv2.INTER_LINEAR: PIL.Image.BILINEAR,
    cv2.INTER_NEAREST: PIL.Image.NEAREST,
    cv2.INTER_CUBIC: PIL.Image.CUBIC,
}

INTER_CV_TO_TCH = {
    cv2.INTER_LINEAR: 'bilinear',
    cv2.INTER_NEAREST: 'nearest',
    cv2.INTER_CUBIC: 'bicubic',
}


COLORSPACE_MAPPING = {
    (COLORSPACE.BGR, COLORSPACE.RGB): cv2.COLOR_BGR2RGB,
    (COLORSPACE.RGB, COLORSPACE.BGR): cv2.COLOR_RGB2BGR,
    (COLORSPACE.BGR, COLORSPACE.GRAY): cv2.COLOR_BGR2GRAY,
    (COLORSPACE.RGB, COLORSPACE.GRAY): cv2.COLOR_RGB2GRAY,

    (COLORSPACE.GRAY, COLORSPACE.RGB): cv2.COLOR_GRAY2RGB,
    (COLORSPACE.GRAY, COLORSPACE.BGR): cv2.COLOR_GRAY2BGR,

    (COLORSPACE.RGB, COLORSPACE.BT709_FULLRANGE): 'RGB_TO_YUV_BT709_FULLRANGE',
    (COLORSPACE.BGR, COLORSPACE.BT709_FULLRANGE): 'BGR_TO_YUV_BT709_FULLRANGE',
    (COLORSPACE.RGB, COLORSPACE.BT709_VIDEORANGE): 'RGB_TO_YUV_BT709_VIDEORANGE',
    (COLORSPACE.BGR, COLORSPACE.BT709_VIDEORANGE): 'BGR_TO_YUV_BT709_VIDEORANGE',

    (COLORSPACE.BT709_FULLRANGE, COLORSPACE.RGB): 'YUV_BT709_FULLRANGE_TO_RGB',
    (COLORSPACE.BT709_FULLRANGE, COLORSPACE.BGR): 'YUV_BT709_FULLRANGE_TO_BGR',
    (COLORSPACE.BT709_VIDEORANGE, COLORSPACE.RGB): 'YUV_BT709_VIDEORANGE_TO_RGB',
    (COLORSPACE.BT709_VIDEORANGE, COLORSPACE.BGR): 'YUV_BT709_VIDEORANGE_TO_BGR',

    (COLORSPACE.BGR, COLORSPACE.HSV): cv2.COLOR_BGR2HSV,
    (COLORSPACE.HSV, COLORSPACE.BGR): cv2.COLOR_HSV2BGR,
    (COLORSPACE.RGB, COLORSPACE.HSV): cv2.COLOR_RGB2HSV,
    (COLORSPACE.HSV, COLORSPACE.RGB): cv2.COLOR_HSV2RGB,
}

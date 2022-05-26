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
"""MORPHOLOGY
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


#!<-----------------------------------------------------------------------------
#!< TRIMAP
#!<-----------------------------------------------------------------------------


def _alpha_to_trimap_np(alpha: np.array, erode_step=10, dilate_step=10, **kwargs):
  alpha = alpha.astype('uint8')
  fg_mask = np.array(np.equal(alpha, 255).astype(np.float32))
  unknown = np.array(np.not_equal(alpha, 0).astype(np.float32))
  kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
  fg_mask = cv2.erode(fg_mask, kernel, erode_step)
  unknown = cv2.dilate(unknown, kernel, dilate_step)
  trimap = fg_mask * 255 + (unknown - fg_mask) * 128
  return trimap


@T.MetaWrapper(support=[T.ImageMeta])
def _alpha_to_trimap_meta(metas: Sequence[T.MetaBase], erode_step=10, dilate_step=10, **kwargs):

  for meta in metas:

    if meta.source != T.COLORSPACE.HEATMAP:
      continue

    if isinstance(meta, T.ImageMeta):
      assert meta.bin.ndim == 2, "Require input is a HxW heatmap."
      meta.bin = _alpha_to_trimap_np(meta.bin.astype('uint8'),
                                     erode_step=erode_step,
                                     dilate_step=dilate_step)

  return metas


def alpha_to_trimap(inputs, erode_step=10, dilate_step=10, **kwargs):
  """[summary]

  Args:
      inputs ([type]): [description]
      erode_step (int, optional): [description]. Defaults to 10.
      dilate_step (int, optional): [description]. Defaults to 10.

  Returns:
      [type]: [description]
  """
  if T.IsNumpy(inputs):
    return _alpha_to_trimap_np(inputs, erode_step=erode_step, dilate_step=dilate_step)
  elif T.IsMeta(inputs):
    return _alpha_to_trimap_meta(inputs, erode_step=erode_step, dilate_step=dilate_step, **kwargs)
  elif T.IsTensor(inputs):
    raise NotImplementedError
  elif T.IsPilImage(inputs):
    raise NotImplementedError


def random_alpha_to_trimap(inputs, erode_steps=(1, 20), dilate_steps=(1, 20), **kwargs):
  """[summary]

  Args:
      inputs ([type]): [description]
      erode_steps (list, optional): [description]. Defaults to [1, 20].
      dilate_steps (list, optional): [description]. Defaults to [1, 20].

  Returns:
      [type]: [description]
  """
  erode_step = random.randint(erode_steps[0], erode_steps[1])
  dilate_step = random.randint(dilate_steps[0], dilate_steps[1])
  return alpha_to_trimap(inputs, erode_step=erode_step, dilate_step=dilate_step, **kwargs)

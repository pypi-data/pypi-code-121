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
r"""augmentation based on PIL library, it should compatable with torchvision.

  Pair transforms are MODs of regular transforms so that it takes in multiple images
and apply exact transforms on all images. This is especially useful when we want the
transforms on a pair of images.

Example:
    img1, img2, ..., imgN = transforms(img1, img2, ..., imgN)

"""
import math
import random
import torch
import numpy as np

from PIL import Image, ImageFilter

from torchvision.transforms import *
from torchvision.transforms.functional import *


class PairCompose(Compose):

  def __call__(self, *x):
    for transform in self.transforms:
      x = transform(*x)
    return x


class PairApply:

  def __init__(self, transforms):
    self.transforms = transforms

  def __call__(self, *x):
    return [self.transforms(xi) for xi in x]


class PairApplyOnlyAtIndices:

  def __init__(self, indices, transforms):
    self.indices = indices
    self.transforms = transforms

  def __call__(self, *x):
    return [self.transforms(xi) if i in self.indices else xi for i, xi in enumerate(x)]


class PairRandomAffine(RandomAffine):

  def __init__(self, degrees, translate=None, scale=None, shear=None, resamples=None, fillcolor=0):
    super().__init__(degrees, translate, scale, shear, Image.NEAREST, fillcolor)
    self.resamples = resamples

  def __call__(self, *x):
    if not len(x):
      return []
    param = self.get_params(self.degrees, self.translate, self.scale, self.shear, x[0].size)
    resamples = self.resamples or [self.resample] * len(x)
    return [affine(xi, *param, resamples[i], self.fillcolor) for i, xi in enumerate(x)]


class PairRandomHorizontalFlip(RandomHorizontalFlip):

  def __call__(self, *x):
    if torch.rand(1) < self.p:
      x = [hflip(xi) for xi in x]
    return x


class RandomBoxBlur:

  def __init__(self, prob, max_radius):
    self.prob = prob
    self.max_radius = max_radius

  def __call__(self, img):
    if torch.rand(1) < self.prob:
      fil = ImageFilter.BoxBlur(random.choice(range(self.max_radius + 1)))
      img = img.filter(fil)
    return img


class PairRandomBoxBlur(RandomBoxBlur):

  def __call__(self, *x):
    if torch.rand(1) < self.prob:
      fil = ImageFilter.BoxBlur(random.choice(range(self.max_radius + 1)))
      x = [xi.filter(fil) for xi in x]
    return x


class RandomSharpen:

  def __init__(self, prob):
    self.prob = prob
    self.filter = ImageFilter.SHARPEN

  def __call__(self, img):
    if torch.rand(1) < self.prob:
      img = img.filter(self.filter)
    return img


class PairRandomSharpen(RandomSharpen):

  def __call__(self, *x):
    if torch.rand(1) < self.prob:
      x = [xi.filter(self.filter) for xi in x]
    return x


class PairRandomAffineAndResize:

  def __init__(self, size, degrees, translate, scale, shear, ratio=(
          3. / 4., 4. / 3.), resample=Image.BILINEAR, fillcolor=0):
    self.size = size
    self.degrees = degrees
    self.translate = translate
    self.scale = scale
    self.shear = shear
    self.ratio = ratio
    self.resample = resample
    self.fillcolor = fillcolor

  def __call__(self, *x):
    if not len(x):
      return []

    w, h = x[0].size
    scale_factor = max(self.size[1] / w, self.size[0] / h)

    w_padded = max(w, self.size[1])
    h_padded = max(h, self.size[0])

    pad_h = int(math.ceil((h_padded - h) / 2))
    pad_w = int(math.ceil((w_padded - w) / 2))

    scale = self.scale[0] * scale_factor, self.scale[1] * scale_factor
    translate = self.translate[0] * scale_factor, self.translate[1] * scale_factor
    affine_params = RandomAffine.get_params(self.degrees, translate, scale, self.shear, (w, h))

    def transform(img):
      if pad_h > 0 or pad_w > 0:
        img = pad(img, (pad_w, pad_h))

      img = affine(img, *affine_params, self.resample, self.fillcolor)
      img = center_crop(img, self.size)
      return img

    return [transform(xi) for xi in x]


class RandomAffineAndResize(PairRandomAffineAndResize):

  def __call__(self, img):
    return super().__call__(img)[0]

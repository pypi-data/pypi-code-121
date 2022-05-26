# Copyright 2021 The KaiJIN Authors. All Rights Reserved.
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
r"""torchvision like dataset: using PIL as transform
"""

import os
import glob
from typing import List

import cv2
import torch
from PIL import Image

from tw import logger


class ImagesDataset(torch.utils.data.Dataset):

  r"""Loading all jpg/png images at path folder.
  """

  def __init__(self, path, mode='RGB', transform=None):
    self.transform = transform
    self.mode = mode

    # collect jpg / png images
    self.filenames = sorted([
        *glob.glob(os.path.join(path, '**', '*.jpg'), recursive=True),
        *glob.glob(os.path.join(path, '**', '*.png'), recursive=True),
        *glob.glob(os.path.join(path, '**', '*.JPEG'), recursive=True),
    ])

    logger.info(f'Total loading {len(self.filenames)} images from {path}.')

  def __len__(self):
    return len(self.filenames)

  def __getitem__(self, idx):

    with Image.open(self.filenames[idx]) as img:
      img = img.convert(self.mode)

    if self.transform:
      img = self.transform(img)

    return img


class VideoDataset(torch.utils.data.Dataset):

  def __init__(self, path: str, transform: any = None):

    self.cap = cv2.VideoCapture(path)
    self.transform = transform

    self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    self.frame_rate = self.cap.get(cv2.CAP_PROP_FPS)
    self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    logger.info(f'Loading {self.frame_count} frames from {path}.')

  def __len__(self):
    return self.frame_count

  def __getitem__(self, idx):

    # return a clip
    if isinstance(idx, slice):
      return [self[i] for i in range(*idx.indices(len(self)))]

    if self.cap.get(cv2.CAP_PROP_POS_FRAMES) != idx:
      self.cap.set(cv2.CAP_PROP_POS_FRAMES, idx)

    ret, img = self.cap.read()
    if not ret:
      raise IndexError(f'Idx: {idx} out of length: {len(self)}')

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)

    if self.transform:
      img = self.transform(img)

    return img

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_value, exc_traceback):
    self.cap.release()


class SampleDataset(torch.utils.data.Dataset):

  r"""Sample data with interval of samples.
  """

  def __init__(self, dataset, samples):
    samples = min(samples, len(dataset))
    self.dataset = dataset
    self.indices = [i * int(len(dataset) / samples) for i in range(samples)]

  def __len__(self):
    return len(self.indices)

  def __getitem__(self, idx):
    return self.dataset[self.indices[idx]]


class ZipDataset(torch.utils.data.Dataset):

  def __init__(self, datasets: List[torch.utils.data.Dataset], transform=None, assert_equal_length=False):
    self.datasets = datasets
    self.transform = transform

    if assert_equal_length:
      for i in range(1, len(datasets)):
        assert len(datasets[i]) == len(datasets[i - 1]), 'Datasets are not equal in length.'

  def __len__(self):
    return max(len(d) for d in self.datasets)

  def __getitem__(self, idx):
    x = tuple(d[idx % len(d)] for d in self.datasets)
    if self.transform:
      x = self.transform(*x)
    return x

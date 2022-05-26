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
import torch
import tw
import tw.transform as T


class Avec2014(torch.utils.data.Dataset):
  r"""Avec2014 dataset"""

  def __init__(self, path, transform, **kwargs):
    tw.fs.raise_path_not_exist(path)
    root = os.path.dirname(path)

    self.targets = []
    with open(path) as fp:
      for line in fp:
        res = line.split(' ')
        folder = '{}/frames/{}'.format(root, res[0])
        degree = int(res[1])
        for fname in os.listdir(folder):
          img_path = os.path.join(folder, fname)
          if not os.path.exists(img_path):
            tw.logger.warn(img_path + ' not found.')
          self.targets.append((img_path, degree))

    self.transform = transform
    tw.logger.info("Total load %d images." % len(self))

  def __len__(self):
    return len(self.targets)

  def __getitem__(self, idx):
    img_meta = T.ImageMeta(path=self.targets[idx][0], source=T.COLORSPACE.BGR)
    img_meta.label = self.targets[idx][1]
    return self.transform([img_meta.load().numpy()])


class Avec2014Video(torch.utils.data.Dataset):

  def __init__(self, path, transform, num_frame=16, num_interval=8, overlap=0.5, **kwargs):
    """AVEC2014 Video Dataset.

    Args:
        path ([type]): [description]
        transform ([type]): [description]
        num_frame (int, optional): [description]. Defaults to 16.
        num_interval (int, optional): [description]. Defaults to 8.
        overlap (float, optional): [description]. Defaults to 0.5.

    """

    tw.fs.raise_path_not_exist(path)
    root = os.path.dirname(path)

    self.identity = []
    with open(path) as fp:
      for line in fp:
        res = line.split(' ')
        folder = '{}/frames/{}'.format(root, res[0])
        degree = int(res[1])
        self.identity.append((folder, degree))

    self.targets = []
    overlap = int(num_frame * overlap)
    for folder, degree in self.identity:
      filelist = []

      # collect images from every subfolder
      for fname in sorted(os.listdir(folder)):
        img_path = os.path.join(folder, fname)
        if not os.path.exists(img_path):
          tw.logger.warn(path + ' not found.')
        if img_path.endswith('.jpg'):
          filelist.append(img_path)

      # squences with interval
      frange = num_frame * num_interval
      for i in range(frange, len(filelist), overlap * num_interval):
        self.targets.append((filelist[i - frange: i: num_interval], degree))

    self.transform = transform
    tw.logger.info("Total load %d sequences." % len(self))

  def __len__(self):
    return len(self.targets)

  def __getitem__(self, idx):
    vid_meta = T.VideoMeta(path=self.targets[idx][0], source=T.COLORSPACE.BGR)
    vid_meta.label = self.targets[idx][1]
    return self.transform([vid_meta.load().numpy()])

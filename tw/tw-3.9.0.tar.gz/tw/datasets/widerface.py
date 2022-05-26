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
"""WiderFace
"""
import os
import torch
import random
import tw
import tw.transform as T


class WiderFace(torch.utils.data.Dataset):

  """dataset could be downloaded from:

    https://github.com/biubug6/Pytorch_Retinaface

    we use the protocal offered by this repo, which includes:
      1. bounding box info.
      2. five pts landmarks.

    For example:
      # 0--Parade/0_Parade_marchingband_1_849.jpg
      449 330 122 149 488.906 373.643 0.0 542.089 376.442 0.0 515.031 412.83 0.0 485.174 425.893 0.0 538.357 431.491 0.0 0.82
      # 0--Parade/0_Parade_Parade_0_904.jpg
      ...

  """

  def __init__(self, path, transform, **kwargs):
    super().__init__()

    tw.fs.raise_path_not_exist(path)
    root = os.path.dirname(os.path.abspath(path))

    self.targets = []

    with open(path) as fp:
      for line in fp:
        line = line.replace('\n', '')

        if line.startswith('#'):
          filepath = line[2:]
          filepath = os.path.join(root, 'images', filepath)
          assert os.path.exists(filepath), filepath
          self.targets.append({
              'path': filepath,
              'metas': []
          })

        else:
          self.targets[-1]['metas'].append([float(i) for i in line.split(' ')])

    self.transform = transform

  def __len__(self):
    return len(self.targets)

  def __getitem__(self, idx):

    # path, bbox, landmarks
    ins = self.targets[idx]
    path = ins['path']

    # preload image
    img_meta = T.ImageMeta(path=path)
    img_meta.load()

    # set bbox attr
    bbox_meta = T.BoxListMeta()
    bbox_meta.set_affine_size(img_meta.h, img_meta.w)

    # set landmark attr
    pts_meta = T.KpsListMeta()
    pts_meta.set_affine_size(img_meta.h, img_meta.w)

    # collect info
    for meta in ins['metas']:

      # fix
      if meta[4] < 0:
        label = -1  # without landmarks
      else:
        label = 1  # with landmarks

      # add bounding box
      bbox_meta.add(meta[0], meta[1], meta[2] + meta[0], meta[3] + meta[1], label=label)

      # add landmarks
      pts_meta.add(meta[4], meta[5])
      pts_meta.add(meta[7], meta[8])
      pts_meta.add(meta[10], meta[11])
      pts_meta.add(meta[13], meta[14])
      pts_meta.add(meta[16], meta[17])

    if self.transform:
      return self.transform([img_meta.numpy(), bbox_meta.numpy(), pts_meta.numpy()])
    else:
      return [img_meta.numpy(), bbox_meta.numpy(), pts_meta.numpy()]


class WiderFaceTest(torch.utils.data.Dataset):

  """dataset could be downloaded from:

    https://github.com/biubug6/Pytorch_Retinaface

    widerface/val/
     - wider_val.txt
     - images/
      - 0--Parade
      - ...

    For example:
      /24--Soldier_Firing/24_Soldier_Firing_Soldier_Firing_24_329.jpg
      /24--Soldier_Firing/24_Soldier_Firing_Soldier_Firing_24_10.jpg
      ...

  """

  def __init__(self, path, transform, **kwargs):
    super().__init__()

    tw.fs.raise_path_not_exist(path)
    root = os.path.dirname(os.path.abspath(path))

    self.targets = []
    with open(path) as fp:
      for line in fp:
        line = line.replace('\n', '')[1:]  # skip '/'
        filepath = os.path.join(root, 'images', line)
        assert os.path.exists(filepath), filepath
        self.targets.append((filepath, line))

    self.transform = transform
    tw.logger.info("Total load %d images." % len(self))

  def __len__(self):
    return len(self.targets)

  def __getitem__(self, idx):

    # path, bbox, landmarks
    path = self.targets[idx]
    # preload image
    img_meta = T.ImageMeta(path=path[0])
    img_meta.load()
    img_meta.caption = path[1]

    if self.transform:
      return self.transform([img_meta.numpy()])
    else:
      return [img_meta.numpy()]

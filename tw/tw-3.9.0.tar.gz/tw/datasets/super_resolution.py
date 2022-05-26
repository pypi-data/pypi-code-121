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
"""Image or Video Super Resolution Dataset
"""
import copy
import os
from collections import OrderedDict
import torch
import scipy
import numpy as np
import tw
import tw.transform as T


class BSD300():
  pass


class Set14():
  pass


class Flickr1024(torch.utils.data.Dataset):

  """Flickr1024 dataset for Stereo-Image-Super-Resolution: 
    https://codalab.lisn.upsaclay.fr/competitions/1598#participate

    e.g. super resolution

    Format(binary):
      data = {
        'LLR': [n, h, w, 3],
        'RLR': [n, h, w, 3],
        'LHR': [n, h * 4, w * 4, 3],
        'RHR': [n, h * 4, w * 4, 3],
      }
      patch is used in np.ndarray (BGR 0-255 format)

    Format(path):
      path
      - HR
        - 0001_L.png
        - 0001_R.png
        - ...
      - LR_x4
        - 0001_L.png
        - 0001_R.png

  """

  def __init__(self, path, transform, is_binary=False, repeat=1, phase=tw.phase.train, **kwargs):
    # check path
    tw.fs.raise_path_not_exist(path)
    self.transform = transform
    self.is_binary = is_binary
    self.phase = phase

    if is_binary:
      self.targets = torch.load(path)
      assert self.targets['LLR'].shape[0] == self.targets['RLR'].shape[0]
      assert self.targets['LHR'].shape[0] == self.targets['RHR'].shape[0]

    elif phase == tw.phase.test:
      self.targets = {'LLR': [], 'RLR': []}
      for name in sorted(os.listdir(path)):
        if '.png' not in name:
          continue
        if 'R.png' in name:
          continue
        l_lr_path = os.path.join(path, name)
        r_lr_path = l_lr_path.replace('_L.png', '_R.png')
        assert os.path.exists(l_lr_path) and os.path.exists(r_lr_path)
        self.targets['LLR'].append(l_lr_path)
        self.targets['RLR'].append(r_lr_path)

    else:
      self.targets = {'LLR': [], 'RLR': [], 'LHR': [], 'RHR': []}
      for name in sorted(os.listdir(os.path.join(path, 'HR'))):
        if '.png' not in name:
          continue
        if 'R.png' in name:
          continue
        l_hr_path = os.path.join(path, 'HR', name)
        r_hr_path = l_hr_path.replace('_L.png', '_R.png')
        l_lr_path = l_hr_path.replace('HR', 'LR_x4')
        r_lr_path = r_hr_path.replace('HR', 'LR_x4')
        assert os.path.exists(l_hr_path) and os.path.exists(r_hr_path) and os.path.exists(l_lr_path) and os.path.exists(r_lr_path)  # nopep8
        for _ in range(repeat):
          self.targets['LHR'].append(l_hr_path)
          self.targets['RHR'].append(r_hr_path)
          self.targets['LLR'].append(l_lr_path)
          self.targets['RLR'].append(r_lr_path)

    tw.logger.info('Total loading %d samples.' % len(self))

  def __len__(self):
    return len(self.targets['LLR'])

  def __getitem__(self, idx):
    if self.is_binary:
      left_hr = T.ImageMeta(binary=self.targets['LHR'][idx].copy())
      right_hr = T.ImageMeta(binary=self.targets['RHR'][idx].copy())
      left_lr = T.ImageMeta(binary=self.targets['LLR'][idx].copy())
      right_lr = T.ImageMeta(binary=self.targets['RLR'][idx].copy())
      return self.transform([left_lr, right_lr, left_hr, right_hr])
    elif self.phase == tw.phase.test:
      left_lr = T.ImageMeta(path=self.targets['LLR'][idx])
      left_lr.load().numpy()
      right_lr = T.ImageMeta(path=self.targets['RLR'][idx])
      right_lr.load().numpy()
      return self.transform([left_lr, right_lr])
    else:
      left_hr = T.ImageMeta(path=self.targets['LHR'][idx])
      left_hr.load().numpy()
      right_hr = T.ImageMeta(path=self.targets['RHR'][idx])
      right_hr.load().numpy()
      left_lr = T.ImageMeta(path=self.targets['LLR'][idx])
      left_lr.load().numpy()
      right_lr = T.ImageMeta(path=self.targets['RLR'][idx])
      right_lr.load().numpy()
      return self.transform([left_lr, right_lr, left_hr, right_hr])

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
"""Image or Video Denoise Dataset
"""
import copy
import os
import torch
import scipy
import numpy as np
import tw
import tw.transform as T


class Kodak(torch.utils.data.Dataset):
  """pass
  """

  def __init__(self, path, transform, phase=tw.phase.train):
    """
    """
    tw.fs.raise_path_not_exist(path)


class SIDD_sRGB(torch.utils.data.Dataset):
  """SIDD dataset: https://www.eecs.yorku.ca/~kamel/sidd/benchmark.php

    SIDD
      - SIDD_Medium_Srgb
        - Data [path for phase==tw.phase.train]
          - 0001_001_S6_00100_00060_3200_L
          - 0001_GT_SRGB_010.PNG
          - 0001_GT_SRGB_011.PNG
          - 0001_NOISY_SRGB_010.PNG
          - 0001_NOISY_SRGB_011.PNG
      - SIDD_Medium_Srgb_Val [path for phase==tw.phase.val]
        - ValidationGtBlocksSrgb.mat
        - ValidationNoisyBlocksSrgb.mat

  """

  def __init__(self, path, transform, phase=tw.phase.train):
    """SIDD Dataset.

      For training, offering:
        <scene-instance-number>
        <scene_number>
        <smartphone-code>
        <ISO-level>
        <shutter-speed>
        <illuminant-temperature>
        <illuminant-brightness-code>

    Args:
        path ([type]): see description of SIDD
        transform ([type]): transform method
        phase ([type], optional): dataset
    """
    tw.fs.raise_path_not_exist(path)
    self.targets = []

    if phase == tw.phase.train:
      for fold in os.listdir(path):
        fold_path = os.path.join(path, fold)
        scene, number, phone, iso, shutter, temp, bright = fold.split('_')
        gt1 = f'{scene}_GT_SRGB_010.PNG'
        gt2 = f'{scene}_GT_SRGB_011.PNG'
        in1 = f'{scene}_NOISY_SRGB_010.PNG'
        in2 = f'{scene}_NOISY_SRGB_011.PNG'

        self.targets.append((
            os.path.join(fold_path, in1),
            os.path.join(fold_path, gt1),
            int(number), phone, int(iso), int(shutter), int(temp), bright
        ))

        self.targets.append((
            os.path.join(fold_path, in2),
            os.path.join(fold_path, gt2),
            int(number), phone, int(iso), int(shutter), int(temp), bright
        ))

    elif phase == tw.phase.val:
      gt_path = os.path.join(path, 'ValidationGtBlocksSrgb.mat')
      noise_path = os.path.join(path, 'ValidationNoisyBlocksSrgb.mat')
      tw.fs.raise_path_not_exist(gt_path)
      tw.fs.raise_path_not_exist(noise_path)

      from scipy.io import loadmat

      gt = loadmat(gt_path)['ValidationGtBlocksSrgb']
      noise = loadmat(noise_path)['ValidationNoisyBlocksSrgb']

      assert gt.shape == noise.shape

      # images, #blocks, height, width, #channels
      n, nb, h, w, c = gt.shape

      for i in range(n):
        for j in range(nb):
          self.targets.append((noise[i, j], gt[i, j]))

    else:
      raise NotImplementedError(phase)

    self.phase = phase
    self.transform = transform
    tw.logger.info('Total loading %d pairs image.' % len(self.targets))

  def __len__(self):
    return len(self.targets)

  def __getitem__(self, idx):
    """separate processing
    """

    if self.phase == tw.phase.train:
      noise_meta = T.ImageMeta(path=self.targets[idx][0], source=T.COLORSPACE.BGR)
      gt_meta = T.ImageMeta(path=self.targets[idx][1], source=T.COLORSPACE.BGR)
      noise_meta.caption = self.targets[idx][2:]
      return self.transform([noise_meta.load().numpy(), gt_meta.load().numpy()])

    elif self.phase == tw.phase.val:
      noise_meta = T.ImageMeta(binary=self.targets[idx][0], source=T.COLORSPACE.RGB)
      gt_meta = T.ImageMeta(binary=self.targets[idx][1], source=T.COLORSPACE.RGB)
      return self.transform([noise_meta.numpy(), gt_meta.numpy()])

    else:
      raise NotImplementedError(self.phase)

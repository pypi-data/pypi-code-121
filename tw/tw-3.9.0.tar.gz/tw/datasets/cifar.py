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
import pickle
import torch
import numpy as np
import tw
import tw.transform as T


class Cifar10(torch.utils.data.Dataset):
  r"""Cifar10 dataset
    - data_batch_1
    - data_batch_2
    - data_batch_3
    - data_batch_4
    - data_batch_5
    - test_batch
  """

  def __init__(self, path, transform, phase, **kwargs):

    def unpickle(file):
      with open(file, 'rb') as fo:
        return pickle.load(fo, encoding='bytes')

    targets = []
    if phase == tw.phase.train:
      batchs = ['data_batch_1', 'data_batch_2', 'data_batch_3', 'data_batch_4', 'data_batch_5']
    else:
      batchs = ['test_batch']

    for batch in batchs:
      res = unpickle(os.path.join(path, batch))
      imgs = res[b'data']  # 10000x3072
      imgs = np.reshape(imgs, (10000, 3, 32, 32))
      labels = res[b'labels']
      for img, label in zip(imgs, labels):
        img = np.transpose(img, (1, 2, 0))
        targets.append((img, label))

    self.targets = targets
    self.transform = transform

  def __len__(self):
    return len(self.targets)

  def __getitem__(self, idx):
    img_meta = T.ImageMeta(binary=self.targets[idx][0].copy())
    img_meta.label = self.targets[idx][1]
    return self.transform([img_meta.load().numpy()])

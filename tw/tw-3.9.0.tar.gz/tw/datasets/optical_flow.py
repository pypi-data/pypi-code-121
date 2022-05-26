# Copyright 2022 The KaiJIN Authors. All Rights Reserved.
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
""" optical flow network
"""
import copy
import glob
import os
from collections import OrderedDict
import torch
import scipy
import numpy as np
import tw
import tw.transform as T


class MPISintel(torch.utils.data.Dataset):

  """MPI-Sintel dataset

    path: _datasets/optical_flow/MPI-Sintel
     - training
      - albedo
      - clean
      - final
      - flow
      - flow_viz
      - invalid
      - occlusions
     - test
      - clean
      - final

  """

  def __init__(self, path, transform, phase, subset='clean', repeat=1, **kwargs):
    # check
    self.subset = subset
    self.targets = []
    self.method = None

    flow_root = os.path.join(path, 'training', 'flow')
    flow_list = sorted(glob.glob(os.path.join(flow_root, '*/*.flo')))
    for flow in flow_list:
      idx = os.path.basename(flow)[6:10]
      idx_n = '%04d' % (int(idx) + 1)
      img1 = flow.replace('/flow/', '/{}/'.format(subset)).replace('.flo', '.png')
      img2 = flow.replace(idx, idx_n).replace('/flow/', '/{}/'.format(subset)).replace('.flo', '.png')
      assert os.path.isfile(img1), img1
      assert os.path.isfile(img2), img2
      assert os.path.isfile(flow), flow
      self.targets.append((img1, img2, flow))

    # using all dataset as training / validation
    targets = []
    labels = []
    with open(os.path.join(path, 'Sintel_train_val.txt')) as fp:
      for line in fp:
        labels.append(int(line))
    for i, target in enumerate(self.targets):
      if labels[i] == 1 and phase == tw.phase.train:
        targets.append(target)
      if labels[i] == 2 and phase == tw.phase.val:
        targets.append(target)
    self.targets = targets

    # repeat dataset
    if repeat > 1:
      targets = []
      for _ in range(repeat):
        for target in self.targets:
          targets.append(target)
      self.targets = targets

    self.transform = transform
    tw.logger.info(f'total load num of image: {len(self.targets)}.')

  def __len__(self):
    return len(self.targets)

  def __getitem__(self, idx):
    """fetch elements
    """
    img1, img2, flow = self.targets[idx]

    img1_meta = T.ImageMeta(path=img1, source=T.COLORSPACE.BGR)
    img1_meta.load().numpy()

    img2_meta = T.ImageMeta(path=img2, source=T.COLORSPACE.BGR)
    img2_meta.load().numpy()

    flow = tw.flow.read_flow(flow).astype(np.float32)
    flow_meta = T.ImageMeta(binary=flow, source=T.COLORSPACE.FLOW)

    return self.transform([img1_meta, img2_meta, flow_meta])


class FlyingChairs(torch.utils.data.Dataset):

  """Flying Chairs

    path: _datasets/optical_flow/FlyingChairs/

  """

  def __init__(self, path, transform, phase, repeat=1, **kwargs):
    # check
    self.targets = []
    self.method = None

    flow_root = os.path.join(path, 'data')
    flow_list = sorted(glob.glob(os.path.join(flow_root, '*.flo')))
    for flow in flow_list:
      img1 = flow.replace('_flow.flo', '_img1.ppm')
      img2 = flow.replace('_flow.flo', '_img2.ppm')
      assert os.path.isfile(img1), img1
      assert os.path.isfile(img2), img2
      assert os.path.isfile(flow), flow
      self.targets.append((img1, img2, flow))

    # using all dataset as training / validation
    targets = []
    labels = []
    with open(os.path.join(path, 'FlyingChairs_train_val.txt')) as fp:
      for line in fp:
        labels.append(int(line))
    for i, target in enumerate(self.targets):
      if labels[i] == 1 and phase == tw.phase.train:
        targets.append(target)
      if labels[i] == 2 and phase == tw.phase.val:
        targets.append(target)
    self.targets = targets

    # repeat dataset
    if repeat > 1:
      targets = []
      for _ in range(repeat):
        for target in self.targets:
          targets.append(target)
      self.targets = targets

    self.transform = transform
    tw.logger.info(f'total load num of image: {len(self.targets)}.')

  def __len__(self):
    return len(self.targets)

  def __getitem__(self, idx):
    """fetch elements
    """
    img1, img2, flow = self.targets[idx]

    img1_meta = T.ImageMeta(path=img1, source=T.COLORSPACE.BGR)
    img1_meta.load().numpy()

    img2_meta = T.ImageMeta(path=img2, source=T.COLORSPACE.BGR)
    img2_meta.load().numpy()

    flow = tw.flow.read_flow(flow).astype(np.float32)
    flow_meta = T.ImageMeta(binary=flow, source=T.COLORSPACE.FLOW)

    return self.transform([img1_meta, img2_meta, flow_meta])


class FlyingThings3D(torch.utils.data.Dataset):

  """FlyingThings3D

    path: _datasets/optical_flow/FlyingThings3D/
      - frames_cleanpass
        - TRAIN
          - A
            - 0000
              - left
              - right
            - ...
          - ..
        - TEST
      - frames_finalpass
      - optical_flow
        - TRAIN
          - A
            - 0000
              - into_past
                - left
                - right
              - into_future
        - TEST

  """

  def __init__(self, path, transform, phase, repeat=1, **kwargs):
    # check
    self.targets = []
    self.method = None

    imgs_dirs = []
    flow_fw_dirs = []
    flow_bw_dirs = []
    subfold = 'TRAIN' if phase == tw.phase.train else 'TEST'

    for pass_dir in ['frames_cleanpass', 'frames_finalpass']:
      for scene in ['left', ]:  # only use left for training
        folders = glob.glob(os.path.join(path, pass_dir, subfold + '/*/*'))
        folders = [os.path.join(f, scene) for f in folders]
        imgs_dirs += folders

        folders = glob.glob(os.path.join(path, 'optical_flow', subfold + '/*/*/into_future'))
        folders = [os.path.join(f, scene) for f in folders]
        flow_fw_dirs += folders

        folers = glob.glob(os.path.join(path, 'optical_flow', subfold + '/*/*/into_past'))
        folers = [os.path.join(f, scene) for f in folers]
        flow_bw_dirs += folers

    for idir, fw_dir, bw_dir in zip(imgs_dirs, flow_fw_dirs, flow_bw_dirs):
      img_filenames = sorted(os.listdir(idir))
      fw_filenames = sorted(os.listdir(fw_dir))
      bw_filenames = sorted(os.listdir(bw_dir))
      # forward flow
      for img1, img2, fw_name in zip(img_filenames[:-1], img_filenames[1:], fw_filenames[:-1]):
        self.targets.append((os.path.join(idir, img1), os.path.join(idir, img2), os.path.join(fw_dir, fw_name)))
      # backward flow
      for img1, img2, bw_name in zip(img_filenames[1:], img_filenames[:-1], bw_filenames[1:]):
        self.targets.append((os.path.join(idir, img1), os.path.join(idir, img2), os.path.join(bw_dir, bw_name)))

      break

    # repeat dataset
    if repeat > 1:
      targets = []
      for _ in range(repeat):
        for target in self.targets:
          targets.append(target)
      self.targets = targets

    self.transform = transform
    tw.logger.info(f'total load num of image: {len(self.targets)}.')

  def __len__(self):
    return len(self.targets)

  def __getitem__(self, idx):
    """fetch elements
    """
    img1, img2, flow = self.targets[idx]

    img1_meta = T.ImageMeta(path=img1, source=T.COLORSPACE.BGR)
    img1_meta.load().numpy()

    img2_meta = T.ImageMeta(path=img2, source=T.COLORSPACE.BGR)
    img2_meta.load().numpy()

    flow = tw.flow.read_pfm(flow).astype(np.float32)
    flow_meta = T.ImageMeta(binary=flow, source=T.COLORSPACE.FLOW)

    return self.transform([img1_meta, img2_meta, flow_meta])

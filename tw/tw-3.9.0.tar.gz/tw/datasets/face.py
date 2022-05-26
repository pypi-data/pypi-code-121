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
import tqdm
import torch
import random

import numpy as np
import cv2

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


class Face300W(torch.utils.data.Dataset):
  """Ref: https://paperswithcode.com/dataset/300w

    path_to_300w:
      - afw/
      - helen/
      - ibug/
      - lfpw/

    Args:
      path: _datasets/face_alignment/300W
      transform: [ImageMeta, KpsMeta]

    Returns:
      image [h, w, c] (0 - 255 BGR)
      landmark [68, 2] (x1, y1, x2, y2)

  """

  def __init__(self, path, transform, phase, subset='full', **kwargs):
    # check
    self.transform = transform
    self.targets = []
    assert subset in ['full', 'common', 'challenge']
    assert os.path.exists(path), f"Failed to find {path}"

    if phase == tw.phase.train:
      folders = ['afw', 'helen/trainset', 'lfpw/trainset']
    else:
      folders = ['helen/testset', 'lfpw/testset', 'ibug']

    # load image and annotation
    for folder in folders:
      tw.logger.info(f'Load 300W dataset sub-folder: {folder}')

      if subset == 'common' and 'ibug' in folder:
        continue

      if subset == 'challenge' and 'ibug' not in folder:
        continue

      fold_path = os.path.join(path, folder)
      all_files = sorted(os.listdir(fold_path))
      image_files = [x for x in all_files if '.pts' not in x]
      label_files = [x for x in all_files if '.pts' in x]
      assert len(image_files) == len(label_files)

      for image_name, label_name in zip(image_files, label_files):
        image_path = os.path.join(fold_path, image_name)
        label_path = os.path.join(fold_path, label_name)
        self.targets.append(self.load(image_path, label_path))

    tw.logger.info(f'Totally loading {len(self.targets)} samples.')

  def load(self, image_path, label_path, scale=1.1):
    """load image and label
    """
    assert os.path.exists(image_path)
    assert os.path.exists(label_path)

    label_file = open(label_path, 'r')

    anno = label_file.readlines()[3:-1]
    anno = [x.strip().split() for x in anno]
    anno = [[int(float(x[0])), int(float(x[1]))] for x in anno]

    image = cv2.imread(image_path)
    image_height, image_width, _ = image.shape
    anno_x = [x[0] for x in anno]
    anno_y = [x[1] for x in anno]

    bbox_xmin = min(anno_x)
    bbox_ymin = min(anno_y)
    bbox_xmax = max(anno_x)
    bbox_ymax = max(anno_y)

    bbox_width = bbox_xmax - bbox_xmin
    bbox_height = bbox_ymax - bbox_ymin

    bbox_xmin -= int((scale - 1) / 2 * bbox_width)
    bbox_ymin -= int((scale - 1) / 2 * bbox_height)
    bbox_width *= scale
    bbox_height *= scale
    bbox_width = int(bbox_width)
    bbox_height = int(bbox_height)

    bbox_xmin = max(bbox_xmin, 0)
    bbox_ymin = max(bbox_ymin, 0)
    bbox_width = min(bbox_width, image_width - bbox_xmin - 1)
    bbox_height = min(bbox_height, image_height - bbox_ymin - 1)

    anno = [[(x - bbox_xmin) / bbox_width, (y - bbox_ymin) / bbox_height] for x, y in anno]

    bbox_xmax = bbox_xmin + bbox_width
    bbox_ymax = bbox_ymin + bbox_height
    image_crop = image[bbox_ymin: bbox_ymax, bbox_xmin: bbox_xmax, :]

    label_file.close()
    return image_crop, anno

  def __len__(self):
    return len(self.targets)

  def __getitem__(self, idx):
    """fetch elements
    """
    image, pts = self.targets[idx]
    h, w, _ = image.shape

    img_meta = T.ImageMeta(binary=image)
    img_meta.numpy()

    pts_meta = T.KpsListMeta()
    pts_meta.set_affine_size(max_h=h, max_w=w)
    for x, y in pts:
      pts_meta.add(x, y)
    pts_meta.numpy()

    return self.transform([img_meta, pts_meta])


class COFW(torch.utils.data.Dataset):
  """Ref: http://www.vision.caltech.edu/xpburgos/ICCV13/#dataset

    Training set with xx images, each of 29 landmarks.
    Test set with xx images, each of 29 landmarks.


    Args:
      path: _datasets/face_alignment/COFW/COFW_train_color.mat
      transform: [ImageMeta, KpsMeta]

    Returns:
      image [h, w, c] (0 - 255 BGR)
      landmark [29, 2] (x1, y1, x2, y2)

  """

  def __init__(self, path, transform, phase, **kwargs):
    # check
    self.transform = transform
    self.targets = []

    import hdf5storage

    mat = hdf5storage.loadmat(path)

    if phase == tw.phase.train:
      images = mat['IsTr']
      bboxes = mat['bboxesTr']
      annos = mat['phisTr']
    else:
      images = mat['IsT']
      bboxes = mat['bboxesT']
      annos = mat['phisT']

    for i in range(images.shape[0]):
      image = images[i, 0]

      if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
      else:
        image = image[:, :, ::-1]  # RGB to BGR

      bbox = bboxes[i, :]
      anno = annos[i, :]

      image_height, image_width, _ = image.shape
      anno_x = anno[:29]
      anno_y = anno[29: 58]

      xmin, ymin, width, height = bbox
      xmax = xmin + width - 1
      ymax = ymin + height - 1

      xmin = max(xmin, 0)
      ymin = max(ymin, 0)
      xmax = min(xmax, image_width - 1)
      ymax = min(ymax, image_height - 1)
      anno_x = (anno_x - xmin) / (xmax - xmin)
      anno_y = (anno_y - ymin) / (ymax - ymin)
      anno = np.concatenate([anno_x.reshape(-1, 1), anno_y.reshape(-1, 1)], axis=1)
      anno = list(anno)
      anno = [list(x) for x in anno]
      image_crop = image[int(ymin):int(ymax), int(xmin):int(xmax), :]

      self.targets.append((image_crop, np.array(anno)))

    tw.logger.info(f'Totally loading {len(self.targets)} samples.')

  def __len__(self):
    return len(self.targets)

  def __getitem__(self, idx):
    """fetch elements
    """
    image, pts = self.targets[idx]
    h, w, _ = image.shape

    img_meta = T.ImageMeta(binary=image)
    img_meta.numpy()

    pts_meta = T.KpsListMeta()
    pts_meta.set_affine_size(max_h=h, max_w=w)
    for x, y in pts:
      pts_meta.add(x, y)
    pts_meta.numpy()

    return self.transform([img_meta, pts_meta])


class JD106(torch.utils.data.Dataset):
  """Ref: http://www.vision.caltech.edu/xpburgos/ICCV13/#dataset

    JD106:
     - Corrected_landmark
     - Test
     - Training_data
     - training_dataset_face_detection_bounding_box

    Args:
      path: _datasets/face_alignment/JD106
      transform: [ImageMeta, KpsMeta]

    Returns:
      image [h, w, c] (0 - 255 BGR)
      landmark [106, 2] (x1, y1, x2, y2)

  """

  def __init__(self, path, transform, phase, **kwargs):
    # check
    self.transform = transform
    self.targets = []

    fold_corrected = os.path.join(path, 'Corrected_landmark')
    fold_test = os.path.join(path, 'Test')
    fold_train = os.path.join(path, 'Training_data')
    fold_train_bbox = os.path.join(path, 'training_dataset_face_detection_bounding_box')

    bboxes = {}
    for name in os.listdir(fold_train_bbox):
      bboxes[name[:-5]] = os.path.join(fold_train_bbox, name)

    corrected = {}
    for name in os.listdir(fold_corrected):
      corrected[name[:-4]] = os.path.join(fold_corrected, name)

    if phase == tw.phase.train:
      images = {}
      for folder in ['AFW', 'HELEN', 'IBUG', 'LFPW']:
        pic_fold = os.path.join(fold_train, folder, 'picture')
        for name in os.listdir(pic_fold):
          path = os.path.join(pic_fold, name)
          landmark = os.path.join(fold_train, folder, 'landmark', name + '.txt')
          if name in corrected:
            landmark = corrected[name]
          bbox = bboxes[name]
          images[name] = {'path': path, 'landmark': landmark, 'rect': bbox}

    elif phase == tw.phase.val:
      images = {}
      pic_fold = os.path.join(fold_test, 'picture')
      for name in os.listdir(pic_fold):
        path = os.path.join(pic_fold, name)
        landmark = os.path.join(fold_test, 'landmark', name + '.txt')
        if name in corrected:
          landmark = corrected[name]
        bbox = os.path.join(fold_test, 'rect', name + '.rect')
        images[name] = {'path': path, 'landmark': landmark, 'rect': bbox}

    else:
      raise NotImplementedError

    for name, meta in images.items():
      self.targets.append(self.load(meta['path'], meta['landmark'], meta['rect']))

    tw.logger.info(f'Totally loading {len(self.targets)} samples.')

  def load(self, img_path, landmark_path, rect_path):
    """load JD106 points protocal

    Args:
        img_path (str):
        landmark_path (str):
        rect_path (str):
    """
    image = cv2.imread(img_path)
    image_height, image_width, _ = image.shape

    # loading landmark
    anno_x, anno_y = [], []
    with open(landmark_path, 'r') as fp:
      for i, line in enumerate(fp):
        if i == 0:
          continue
        x, y = line.split(' ')
        anno_x.append(float(x))
        anno_y.append(float(y))
    anno_x, anno_y = np.array(anno_x), np.array(anno_y)

    # loading bbox
    with open(rect_path, 'r') as fp:
      for line in fp:
        xmin, ymin, xmax, ymax = line.split(' ')
      xmin, ymin, xmax, ymax = int(xmin), int(ymin), int(xmax), int(ymax)

    xmin = max(xmin, 0)
    ymin = max(ymin, 0)
    xmax = min(xmax, image_width - 1)
    ymax = min(ymax, image_height - 1)
    anno_x = (anno_x - xmin) / (xmax - xmin)
    anno_y = (anno_y - ymin) / (ymax - ymin)
    anno = np.concatenate([anno_x.reshape(-1, 1), anno_y.reshape(-1, 1)], axis=1)
    anno = [list(x) for x in list(anno)]
    image_crop = image[int(ymin):int(ymax), int(xmin):int(xmax), :]

    return image_crop, anno

  def __len__(self):
    return len(self.targets)

  def __getitem__(self, idx):
    """fetch elements
    """
    image, pts = self.targets[idx]
    h, w, _ = image.shape

    img_meta = T.ImageMeta(binary=image)
    img_meta.numpy()

    pts_meta = T.KpsListMeta()
    pts_meta.set_affine_size(max_h=h, max_w=w)
    for x, y in pts:
      pts_meta.add(x, y)
    pts_meta.numpy()

    return self.transform([img_meta, pts_meta])

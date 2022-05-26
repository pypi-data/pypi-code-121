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
"""General datasets for common tasks.
"""
import os
import tqdm
import glob
import random
import copy
import torch
import cv2
import tw
import tw.transform as T

#!<----------------------------------------------------------------------------
#!< General Datasets for Classification or Regression
#!<----------------------------------------------------------------------------


class ImageLabel(torch.utils.data.Dataset):

  """ImageLabel dataset"""

  def __init__(self, path, label_type, transform, **kwargs):
    # check
    assert label_type in [float, int]
    tw.fs.raise_path_not_exist(path)

    # parse
    res, _ = tw.parser.parse_from_text(path, [str, label_type], [True, False])
    self.targets = []
    for path, label in zip(res[0], res[1]):
      self.targets.append((path, label))

    self.transform = transform
    tw.logger.info(f'Totally loading {len(self.targets)} samples.')

  def __len__(self):
    return len(self.targets)

  def __getitem__(self, idx):
    img_meta = T.ImageMeta(path=self.targets[idx][0])
    img_meta.label = self.targets[idx][1]
    img_meta.load().numpy()
    return self.transform([img_meta])


#!<----------------------------------------------------------------------------
#!< General Datasets for Salient Detection
#!<----------------------------------------------------------------------------

class ImageSalientDet(torch.utils.data.Dataset):

  """SalientDet dataset

  Format:
    1. Image: [0, 255] BGR -> float -> [0, 1.0]
    2. Mask: [0, 255] BGR -> float -> [0, 1.0]

  """

  def __init__(self, path, transform, **kwargs):
    # check
    tw.fs.raise_path_not_exist(path)

    res, _ = tw.parser.parse_from_text(path, [str, str], [True, True])  # nopep8
    self.targets = []
    for img_path, mask_path in zip(res[0], res[1]):
      self.targets.append((img_path, mask_path))

    self.transform = transform
    tw.logger.info('Totally loading %d samples.' % len(self.targets))

  def __len__(self):
    return len(self.targets)

  def __getitem__(self, idx):
    # load image
    img_meta = T.ImageMeta(path=self.targets[idx][0])
    img_meta.label = self.targets[idx][1]
    img_meta.load().numpy()
    # load mask
    mask_meta = T.ImageMeta(path=self.targets[idx][1])
    mask_meta.load().numpy()
    return self.transform([img_meta, mask_meta])


#!<----------------------------------------------------------------------------
#!< General Datasets for Image Enhancement
#!<----------------------------------------------------------------------------

class ImagesDataset(torch.utils.data.Dataset):

  """Loading all jpg/png images at path folder.
  """

  def __init__(self, path, transform, is_preload=False, is_meta=True, **kwargs):
    # check
    self.is_preload = is_preload
    self.is_meta = is_meta
    self.targets = []
    self.method = None

    # method-1: path = [lr_folder_list]
    if isinstance(path, list):
      for folder in path:
        image_list, _ = tw.media.collect((folder))
        self.targets.extend(image_list)
      self.method = 'folder_list'

    # method-2 path = protocal file
    elif isinstance(path, str) and os.path.exists(path) and path.endswith(('.txt',)):
      tw.fs.raise_path_not_exist(path)
      res, _ = tw.parser.parse_from_text(path, [str, ], [True, ])
      self.targets = []
      for img_path in res[0]:
        self.targets.append(img_path)
      self.method = 'file'

    else:
      raise NotImplementedError(path)

    if self.is_preload:
      new_targets = []
      for img_path in tqdm.tqdm(self.targets):
        img = cv2.imread(img_path)
        img = img.astype('float32')
        assert img is not None
        new_targets.append(img)
      self.targets = new_targets

    self.transform = transform
    tw.logger.info(f'total load num of image: {len(self.targets)}.')

  def __len__(self):
    return len(self.targets)

  def __getitem__(self, idx):
    """fetch elements
    """
    img = self.targets[idx]

    # preload or not
    if self.is_preload:
      meta = T.ImageMeta(binary=img.copy(), source=T.COLORSPACE.BGR)

    else:
      meta = T.ImageMeta(path=img, source=T.COLORSPACE.BGR)
      meta.load().numpy()

    # meta or not
    if self.is_meta:
      return self.transform([meta, ])
    else:
      return self.transform(meta.bin)


class ImageRestoration(torch.utils.data.Dataset):

  """General Image Restoration: image to image translation

    e.g. super resolution, denoise, sharpeness

    Method-1: path [
      [lr_folder_1, lr_folder_2, ...],
      [hr_folder_1, hr_folder_2, ...],
    ]

    Method-2: protocal.txt
      lr_img_path1 hr_img_path1
      lr_img_path2 hr_img_path2
      ...

    Method-3: binaryfile.pth
      data = {
        'pred': [n, h, w, 3],
        'label': [n, h', w', 3],
      }
      patch is used in np.ndarray (BGR 0-255 format)

    Note: 
      different from ImageFolderEnhance, it first load all image into memory.

  """

  def __init__(self, path, transform, is_preload=False, is_meta=True, repeat=1, **kwargs):
    # check
    self.is_preload = is_preload
    self.is_meta = is_meta
    self.targets = []
    self.method = None

    # method-1: path = [[lr_folder_list], [hr_folder_list]]
    if isinstance(path, list) and len(path) == 2:
      lr_folder_list, hr_folder_list = path
      assert len(lr_folder_list) == len(hr_folder_list)
      for lr_folder, hr_folder in zip(lr_folder_list, hr_folder_list):
        lr_list = [os.path.join(lr_folder, f) for f in sorted(os.listdir(lr_folder))]
        hr_list = [os.path.join(hr_folder, f) for f in sorted(os.listdir(hr_folder))]
        self.targets.extend([*zip(lr_list, hr_list)])
      self.method = 'folder_list'

    # method-2 path = protocal file input-label
    elif isinstance(path, str) and os.path.exists(path) and path.endswith(('.txt',)):
      tw.fs.raise_path_not_exist(path)
      res, _ = tw.parser.parse_from_text(path, [str, str], [True, True])
      self.targets = []
      for lr_path, hr_path in zip(res[0], res[1]):
        self.targets.append((lr_path, hr_path))
      self.method = 'file'

    # method-3 binary file
    elif isinstance(path, str) and os.path.exists(path) and path.endswith(('.pth',)):
      data = torch.load(path)
      assert data['pred'].shape[0] == data['label'].shape[0]
      for i in tqdm.tqdm(range(data['pred'].shape[0])):
        self.targets.append((data['pred'][i], data['label'][i]))

    else:
      raise NotImplementedError(path)

    if self.is_preload:
      new_targets = []
      for lr_path, hr_path in tqdm.tqdm(self.targets):
        lr_img = cv2.imread(lr_path)
        lr_img = lr_img.astype('float32')
        hr_img = cv2.imread(hr_path)
        hr_img = hr_img.astype('float32')
        assert lr_img is not None and hr_img is not None
        new_targets.append((lr_img, hr_img))
      self.targets = new_targets

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
    lr, hr = self.targets[idx]

    # preload or not
    if self.is_preload:
      lr_meta = T.ImageMeta(binary=lr.copy(), source=T.COLORSPACE.BGR)
      hr_meta = T.ImageMeta(binary=hr.copy(), source=T.COLORSPACE.BGR)

    else:
      lr_meta = T.ImageMeta(path=lr, source=T.COLORSPACE.BGR)
      lr_meta.load().numpy()
      hr_meta = T.ImageMeta(path=hr, source=T.COLORSPACE.BGR)
      hr_meta.load().numpy()

    # meta or not
    if self.is_meta:
      return self.transform([lr_meta, hr_meta])
    else:
      return self.transform(lr_meta.bin, hr_meta.bin)


class VideoRestoration(torch.utils.data.Dataset):

  """General Video Folder Enhancement: video to video translation

    e.g. super resolution, denoise, sharpeness

  Format:
    input_video_folder augmented_video_folder

  """

  def __init__(self, path, transform, segment=1, **kwargs):
    # check
    tw.fs.raise_path_not_exist(path)
    res, _ = tw.parser.parse_from_text(path, [str, str], [True, True])  # nopep8

    self.targets = []
    total_img = 0
    for _, (image_folder, enhance_folder) in enumerate(zip(*res)):
      self.targets.append((
          [os.path.join(image_folder, f) for f in sorted(os.listdir(image_folder))],
          [os.path.join(enhance_folder, f) for f in sorted(os.listdir(enhance_folder))],
      ))
      total_img += len(self.targets[-1][0])

    self.transform = transform
    self.segment = segment
    tw.logger.info(f'num of folder: {len(self)}, num of image: {total_img}.')

  def __len__(self):
    return len(self.targets)

  def __getitem__(self, idx):
    # folder
    img, enh = self.targets[idx]
    assert len(img) <= len(enh), f"{len(img)} vs {len(enh)}."

    i = random.randint(0, len(enh) - self.segment)
    img_meta = T.VideoMeta(path=img[i: i + self.segment])
    img_meta.load().numpy()
    enh_meta = T.VideoMeta(path=enh[i: i + self.segment])
    enh_meta.load().numpy()
    return self.transform([img_meta, enh_meta])

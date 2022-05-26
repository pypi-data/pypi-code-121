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
"""COCO Dataset"""
import os
import torch
import random
import numpy as np
import tw
import tw.transform as T


class CocoDetection(torch.utils.data.Dataset):
  """MS Coco Detection <http://mscoco.org/dataset/#detections-challenge2016>
  """

  def __init__(self, root, annotation, transform, phase=tw.phase.train,
               with_bbox=True, with_segm=False, with_kps=False,
               background_offset=1, num_classes=81,
               **kwargs):
    """COCO Detection

    Args:
        root (string): Root directory where images are downloaded to.
        annotation ([type]): Path to json annotation file.
        transform ([type]): [description]
        with_bbox (bool, optional): [description]. Defaults to True.
        with_segm (bool, optional): [description]. Defaults to False.
        with_kps (bool, optional): [description]. Defaults to False.

    """
    super(CocoDetection, self).__init__()

    self._load_bbox = with_bbox
    self._load_segm = with_segm
    self._load_kps = with_kps

    try:
      from pycocotools import coco as cocotools
    except ImportError:
      raise ImportError('Failed to import pycocotools, please `pip install pycocotools')

    # info
    self._coco = cocotools.COCO(annotation)
    self._ids = sorted(list(self._coco.imgs.keys()))

    # filter too small image
    if phase == tw.phase.train:
      min_size = 32
      valid_inds = []
      ids_with_ann = set(_['image_id'] for _ in self._coco.anns.values())
      for idx in self._ids:
        img_info = self._coco.loadImgs([idx])[0]
        # filter images without ground truth
        if idx not in ids_with_ann:
          continue
        # filter images with too small gt
        if min(img_info['width'], img_info['height']) >= min_size:
          valid_inds.append(idx)
      self._ids = valid_inds

    # coco label to contiguous version
    self._cls_contiguous = {}
    # contiguous label to coco
    self._cls_to_coco = {}
    # contiguous class idx to name
    self._cls_to_name = {}

    self._root = root
    self._background_offset = background_offset
    self._num_classes = num_classes
    self._transform = transform

    for idx, (k, v) in enumerate(self._coco.cats.items()):
      self._cls_to_name[idx] = v['name']

    # map discrete coco category to contiguous
    # zero for background
    # NOTE: we consistently set label from 1 to num_classes + 1
    for idx, cat in enumerate(self._coco.loadCats(self._coco.getCatIds())):
      label = idx + 1
      self._cls_contiguous[cat['id']] = label
      self._cls_to_coco[label] = cat['id']

  def __len__(self):
    return len(self._ids)

  def __getitem__(self, idx):
    """get metas: image, bbox, segmentation, labels"""
    img_id = self._ids[idx]
    img = self._coco.loadImgs([img_id])[0]

    # add metas
    ann_ids = self._coco.getAnnIds(imgIds=img_id)
    anns = self._coco.loadAnns(ann_ids)

    # image
    img_meta = T.ImageMeta(path=os.path.join(self._root, img['file_name']))
    img_meta.id = img_id
    img_meta.load()

    # bounding box
    bbox_meta = T.BoxListMeta()
    bbox_meta.set_affine_size(max_h=img['height'], max_w=img['width'])

    # add each
    for ann in anns:
      # The segmentation format depends on whether the instance represents a
      # single object (iscrowd=0 in which case polygons are used) or a
      # collection of objects (iscrowd=1 in which case RLE is used).
      if ann['iscrowd']:
        continue

      # bbox convert to xyxy format.
      x, y, w, h = ann['bbox']

      # filter too small bounding box
      if ann['area'] <= 0 or w < 1 or h < 1:
        continue

      # discrete coco category to contiguous 0 to num_classes
      cat_id = ann['category_id']
      bbox_meta.add(x, y, x + w - 1, y + h - 1,
                    label=self._cls_contiguous[cat_id],
                    caption=self._coco.loadCats([cat_id])[0]['name'],
                    segm=ann['segmentation'],
                    iscrowd=ann['iscrowd'],
                    category=cat_id)

    return self._transform([img_meta.numpy(), bbox_meta.numpy()])

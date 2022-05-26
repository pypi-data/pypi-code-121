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
"""Detection"""
import os
import torch
import numpy as np
from .base import Evaluator

import tw


class CocoEvaluator(Evaluator):

  def __init__(self, annotation, with_bbox=True, with_segm=False, with_kps=False,
               num_classes=81, background_offset=1):
    super().__init__()
    assert os.path.exists(annotation), f'{annotation}'
    try:
      from pycocotools import coco as cocotools
      from pycocotools import cocoeval
      self.cocotools = cocotools
      self.self.cocoeval = self.cocoeval
    except ImportError:
      raise ImportError('Failed to import pycocotools, please `pip install pycocotools')

    self.metrics = []

    self.with_bbox = with_bbox
    self.with_segm = with_segm
    self.with_kps = with_kps

    self.num_classes = num_classes
    self.background_offset = background_offset

    self.coco = self.cocotools.COCO(annotation)
    # self.ids = sorted(list(self.coco.imgs.keys()))

    # coco label to contiguous version
    self.cls_contiguous = {}
    # contiguous label to coco
    self.cls_to_coco = {}
    # map discrete coco category to contiguous
    # zero for background
    # NOTE: we consistently set label from 1 to num_classes + 1
    for idx, cat in enumerate(self.coco.loadCats(self.coco.getCatIds())):
      label = idx + 1
      self.cls_contiguous[cat['id']] = label
      self.cls_to_coco[label] = cat['id']

    # contiguous class idx to name
    self.cls_to_name = {}
    for idx, (k, v) in enumerate(self.coco.cats.items()):
      self.cls_to_name[idx] = v['name']

  def mean(self, arr):
    select = arr >= 0
    if np.sum(select) > 0:
      return np.mean(arr[select])
    else:
      return 0.0

  def reset(self):
    self.metrics.clear()

  def append(self, values):
    """extend coco detection result"""
    self.metrics.extend(values)

  def accumulate(self):

    # local variable
    metrics = self.metrics
    coco = self.coco
    with_bbox = self.with_bbox
    with_segm = self.with_segm
    map_cls_to_coco = self.cls_to_coco
    map_cls_to_name = self.cls_to_name
    num_classes = self.num_classes
    background_offset = self.background_offset

    # accumulate and transform to coco format
    coco_results = []
    for metric in metrics:
      for logit, box, score in zip(metric['logits'], metric['bboxes'], metric['scores']):
        # mask = np.array(masks[i][:, :, np.newaxis], order='F')
        # rle = cocomask.encode(mask)[0]
        # rle['counts'] = rle['counts'].decode('utf-8')
        coco_results.append({
            'image_id': metric['image_id'],
            'category_id': map_cls_to_coco[logit],
            'bbox': box,
            'score': score,
            'segmentation': None
        })

    # feed to coco
    cocoDt = coco.loadRes(coco_results)
    imgIds = coco.getImgIds()

    # evaluate bbox
    reports = {}

    if with_bbox:
      # accumulate bounding box results
      cocoEval = self.cocoeval.COCOeval(coco, cocoDt, 'bbox')
      cocoEval.params.imgIds = imgIds
      cocoEval.evaluate()
      cocoEval.accumulate()
      # cocoEval.summarize()

      # header
      str_inv_cats = '\n{:^5} {:^15} {:^10} {:^10} {:^10} {:^10} {:^10} {:^10}\n'.format(
          'CatID', 'Name', 'mAP', 'AP@0.5', 'AP@S', 'AP@M', 'AP@L', 'mAR')

      # display results for each category
      for i in range(num_classes - background_offset):
        ap = self.mean(cocoEval.eval['precision'][:, :, i, 0, 2])
        ap05 = self.mean(cocoEval.eval['precision'][0, :, i, 0, 2])
        aps = self.mean(cocoEval.eval['precision'][:, :, i, 1, 2])
        apm = self.mean(cocoEval.eval['precision'][:, :, i, 2, 2])
        apl = self.mean(cocoEval.eval['precision'][:, :, i, 3, 2])
        ar = self.mean(cocoEval.eval['recall'][:, i, 0, 2])
        str_inv_cats += '{:^5} {:^15} {:^10.4f} {:^10.4f} {:^10.4f} {:^10.4f} {:^10.4f} {:^10.4f}\n'.format(
            i, map_cls_to_name[i], ap, ap05, aps, apm, apl, ar)
      tw.logger.val('==> For each category: %s' % str_inv_cats)

      # for all cat
      stat = [
          # AP: IoU
          self.mean(cocoEval.eval['precision'][:, :, :, 0, 2]),
          self.mean(cocoEval.eval['precision'][0, :, :, 0, 2]),
          self.mean(cocoEval.eval['precision'][5, :, :, 0, 2]),
          # AP: Area
          self.mean(cocoEval.eval['precision'][:, :, :, 1, 2]),
          self.mean(cocoEval.eval['precision'][:, :, :, 2, 2]),
          self.mean(cocoEval.eval['precision'][:, :, :, 3, 2]),
          # AR: Dets
          self.mean(cocoEval.eval['recall'][:, :, 0, 0]),
          self.mean(cocoEval.eval['recall'][:, :, 0, 1]),
          self.mean(cocoEval.eval['recall'][:, :, 0, 2]),
          # AR: Area
          self.mean(cocoEval.eval['recall'][:, :, 1, 2]),
          self.mean(cocoEval.eval['recall'][:, :, 2, 2]),
          self.mean(cocoEval.eval['recall'][:, :, 3, 2]),
      ]

      tw.logger.val('\n\
  Average Precision  (AP) @[ IoU=0.50:0.95 | area=   all | maxDets=100 ] = {:.4f} \n\
  Average Precision  (AP) @[ IoU=0.50      | area=   all | maxDets=100 ] = {:.4f} \n\
  Average Precision  (AP) @[ IoU=0.75      | area=   all | maxDets=100 ] = {:.4f} \n\
  Average Precision  (AP) @[ IoU=0.50:0.95 | area= small | maxDets=100 ] = {:.4f} \n\
  Average Precision  (AP) @[ IoU=0.50:0.95 | area=medium | maxDets=100 ] = {:.4f} \n\
  Average Precision  (AP) @[ IoU=0.50:0.95 | area= large | maxDets=100 ] = {:.4f} \n\
  Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets=  1 ] = {:.4f} \n\
  Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets= 10 ] = {:.4f} \n\
  Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets=100 ] = {:.4f} \n\
  Average Recall     (AR) @[ IoU=0.50:0.95 | area= small | maxDets=100 ] = {:.4f} \n\
  Average Recall     (AR) @[ IoU=0.50:0.95 | area=medium | maxDets=100 ] = {:.4f} \n\
  Average Recall     (AR) @[ IoU=0.50:0.95 | area= large | maxDets=100 ] = {:.4f} \n'.format(*stat))

      reports.update({
          'bbox_ap': stat[0],
          'bbox_ap_50': stat[1],
          'bbox_ap_75': stat[2],
          'bbox_ap_s': stat[3],
          'bbox_ap_m': stat[4],
          'bbox_ap_l': stat[5]
      })

    # evaluate mask
    if with_segm:
      cocoEval = self.cocoeval.COCOeval(coco, cocoDt, 'segm')
      cocoEval.params.imgIds = imgIds
      cocoEval.evaluate()
      cocoEval.accumulate()
      cocoEval.summarize()

    return reports

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
import numpy as np
import os
import cv2
import time
import torch
from .nets import PNet, RNet, ONet
from .box_utils import nms, calibrate_box, get_image_boxes, convert_to_square
from .first_stage import run_first_stage


class MTCNN():

  def __init__(self, device='cuda',
               pretrain_pnet='_checkpoints/detection/face_detector/mtcnn/pnet.npy',
               pretrain_rnet='_checkpoints/detection/face_detector/mtcnn/rnet.npy',
               pretrain_onet='_checkpoints/detection/face_detector/mtcnn/onet.npy'):
    tstamp = time.time()
    self.device = device
    print('[MTCNN] loading with', self.device)
    self.pnet = PNet(pretrain=pretrain_pnet).to(device)
    self.rnet = RNet(pretrain=pretrain_rnet).to(device)
    self.onet = ONet(pretrain=pretrain_onet).to(device)
    self.pnet.eval()
    self.rnet.eval()
    self.onet.eval()
    print('[MTCNN] finished loading (%.4f sec)' % (time.time() - tstamp))

  def detect_faces(self, image, conf_th=0.8, scales=[1]):

    thresholds = [conf_th - 0.2, conf_th - 0.1, conf_th]
    nms_thresholds = [0.7, 0.7, 0.7]

    with torch.no_grad():

      # STAGE 1

      bounding_boxes = []

      for s in scales:
        boxes = run_first_stage(image, self.pnet, scale=s, threshold=thresholds[0], device=self.device)
        bounding_boxes.append(boxes)

      bounding_boxes = [i for i in bounding_boxes if i is not None]

      if len(bounding_boxes) == 0:
        return [], []

      bounding_boxes = np.vstack(bounding_boxes)

      keep = nms(bounding_boxes[:, 0:5], nms_thresholds[0])
      bounding_boxes = bounding_boxes[keep]
      bounding_boxes = calibrate_box(bounding_boxes[:, 0:5], bounding_boxes[:, 5:])
      bounding_boxes = convert_to_square(bounding_boxes)
      bounding_boxes[:, 0:4] = np.round(bounding_boxes[:, 0:4])

      # STAGE 2

      img_boxes = get_image_boxes(bounding_boxes, image, size=24)
      img_boxes = torch.Tensor(img_boxes).to(self.device)

      output = self.rnet(img_boxes)
      offsets = output[0].cpu().data.numpy()  # shape [n_boxes, 4]
      probs = output[1].cpu().data.numpy()  # shape [n_boxes, 2]

      keep = np.where(probs[:, 1] > thresholds[1])[0]
      bounding_boxes = bounding_boxes[keep]
      bounding_boxes[:, 4] = probs[keep, 1].reshape((-1,))
      offsets = offsets[keep]

      keep = nms(bounding_boxes, nms_thresholds[1])
      bounding_boxes = bounding_boxes[keep]
      bounding_boxes = calibrate_box(bounding_boxes, offsets[keep])
      bounding_boxes = convert_to_square(bounding_boxes)
      bounding_boxes[:, 0:4] = np.round(bounding_boxes[:, 0:4])

      # STAGE 3

      img_boxes = get_image_boxes(bounding_boxes, image, size=48)
      if len(img_boxes) == 0:
        return [], []
      img_boxes = torch.Tensor(img_boxes).to(self.device)
      output = self.onet(img_boxes)
      landmarks = output[0].cpu().data.numpy()  # shape [n_boxes, 10]
      offsets = output[1].cpu().data.numpy()  # shape [n_boxes, 4]
      probs = output[2].cpu().data.numpy()  # shape [n_boxes, 2]

      keep = np.where(probs[:, 1] > thresholds[2])[0]
      bounding_boxes = bounding_boxes[keep]
      bounding_boxes[:, 4] = probs[keep, 1].reshape((-1,))
      offsets = offsets[keep]
      landmarks = landmarks[keep]

      # compute landmark points
      width = bounding_boxes[:, 2] - bounding_boxes[:, 0] + 1.0
      height = bounding_boxes[:, 3] - bounding_boxes[:, 1] + 1.0
      xmin, ymin = bounding_boxes[:, 0], bounding_boxes[:, 1]
      landmarks[:, 0:5] = np.expand_dims(xmin, 1) + np.expand_dims(width, 1) * landmarks[:, 0:5]
      landmarks[:, 5:10] = np.expand_dims(ymin, 1) + np.expand_dims(height, 1) * landmarks[:, 5:10]

      bounding_boxes = calibrate_box(bounding_boxes, offsets)
      keep = nms(bounding_boxes, nms_thresholds[2], mode='min')
      bounding_boxes = bounding_boxes[keep]
      landmarks = landmarks[keep]

    return bounding_boxes, landmarks

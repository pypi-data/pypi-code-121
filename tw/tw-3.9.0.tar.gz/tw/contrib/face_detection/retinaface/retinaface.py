# Copyright 2017 The KaiJIN Authors. All Rights Reserved.
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
import torch

from .data_utils import cfg_mnet
from .data_utils import load_model
from .box_utils import py_cpu_nms
from .box_utils import decode, decode_landm
from .nets import PriorBox


class RetinafaceDetector:
  def __init__(self, net='mnet', device='cuda',
               pretrain='_checkpoints/detection/face_detector/retinaface_mobilenet0.25.pth'):
    self.net = net
    self.device = torch.device(device)
    self.model = load_model(net, pretrain=pretrain).to(self.device)
    self.model.eval()

  def detect_faces(self, img_raw, confidence_threshold=0.9, top_k=5000, nms_threshold=0.4, keep_top_k=750, resize=1):
    img = np.float32(img_raw)
    im_height, im_width = img.shape[:2]
    scale = torch.Tensor([img.shape[1], img.shape[0], img.shape[1], img.shape[0]])
    img -= (104, 117, 123)
    img = img.transpose(2, 0, 1)
    img = torch.from_numpy(img).unsqueeze(0)
    img = img.to(self.device)
    scale = scale.to(self.device)

    # tic = time.time()
    with torch.no_grad():
      loc, conf, landms = self.model(img)  # forward pass
      # print('net forward time: {:.4f}'.format(time.time() - tic))

    priorbox = PriorBox(cfg_mnet, image_size=(im_height, im_width))
    priors = priorbox.forward()
    priors = priors.to(self.device)
    prior_data = priors.data
    boxes = decode(loc.data.squeeze(0), prior_data, cfg_mnet['variance'])
    boxes = boxes * scale / resize
    boxes = boxes.cpu().numpy()
    scores = conf.squeeze(0).data.cpu().numpy()[:, 1]
    landms = decode_landm(landms.data.squeeze(0), prior_data, cfg_mnet['variance'])
    scale1 = torch.Tensor([img.shape[3], img.shape[2], img.shape[3], img.shape[2],
                           img.shape[3], img.shape[2], img.shape[3], img.shape[2],
                           img.shape[3], img.shape[2]])
    scale1 = scale1.to(self.device)
    landms = landms * scale1 / resize
    landms = landms.cpu().numpy()

    # ignore low scores
    inds = np.where(scores > confidence_threshold)[0]
    boxes = boxes[inds]
    landms = landms[inds]
    scores = scores[inds]

    # keep top-K before NMS
    order = scores.argsort()[::-1][:top_k]
    boxes = boxes[order]
    landms = landms[order]
    scores = scores[order]

    # do NMS
    dets = np.hstack((boxes, scores[:, np.newaxis])).astype(np.float32, copy=False)
    keep = py_cpu_nms(dets, nms_threshold)
    # keep = nms(dets, args.nms_threshold,force_cpu=args.cpu)
    dets = dets[keep, :]
    landms = landms[keep]

    # keep top-K faster NMS
    dets = dets[:keep_top_k, :]
    landms = landms[:keep_top_k, :]
    # print(landms.shape)
    # [num_pts, organ, (x, y)]
    landms = landms.reshape((-1, 5, 2))
    # print(landms.shape)
    # landms = landms.transpose((0, 2, 1))
    # print(landms.shape)
    # landms = landms.reshape(-1, 10, )
    # print(landms.shape)

    return dets, landms

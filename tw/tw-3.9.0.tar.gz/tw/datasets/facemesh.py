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
"""FaceMesh Datset
"""
import os
import tqdm
import random
import pickle

import torch
import numpy as np
import cv2
from PIL import Image
from scipy.io import loadmat, savemat
from skimage.io import imread
from skimage.transform import estimate_transform, warp, SimilarityTransform

import tw
import tw.transform as T
from tw import mesh


class NoW(torch.utils.data.Dataset):

  """
    NoW_Dataset:
     - final_release_version
      - detected_face
      - iphone_pictures
     - scans
     - scans_lmks_onlypp

  """

  def __init__(self, path, transform, detector, use_five_anchor=False,
               face_model_lm3d_path='_datasets/facemesh/data/BFM/similarity_Lm3D_all.mat',
               bvt_106pts_vertices_mapping_path='_datasets/facemesh/data/BIGO/BVT_106pts_vertices_mapping.json',
               **kwargs):
    assert detector in ['MTCNN', 'FAN', 'BVT']
    self.detector = detector
    self.transform = transform
    self.use_five_anchor = use_five_anchor
    self.targets = []

    # loading data
    with open(os.path.join(path, 'imagepathsvalidation.txt')) as f:
      data_lines = f.readlines()
    imagefolder = os.path.join(path, 'final_release_version', 'iphone_pictures')
    bboxfolder = os.path.join(path, 'final_release_version', 'detected_face')

    for line in data_lines:
      img_path = os.path.join(imagefolder, line.strip())
      bbox_path = os.path.join(bboxfolder, line.strip().replace('.jpg', '.npy'))
      bbox_data = np.load(bbox_path, allow_pickle=True, encoding='latin1').item()
      self.targets.append((img_path, bbox_data))

    tw.logger.info(f'using {detector} face detector.')
    if self.detector == 'FAN':
      import face_alignment
      self.det = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, flip_input=False, device='cpu')
    elif self.detector == 'MTCNN':
      from mtcnn import MTCNN
      self.det = MTCNN()
    elif self.detector == 'BVT':
      import BVT
      import json
      self.det = BVT.Engine()
      self.det.init_humanface_module(faceDetection=True, faceLandmark=True, advancedLandmark=True)
      with open(bvt_106pts_vertices_mapping_path, 'r') as f:
        self.lm_map = json.load(f)
    else:
      raise NotImplementedError(self.detector)

    # loading standard facemodel
    self.ldmk3d = mesh.load_bfm_ldmk3d(face_model_lm3d_path, use_five_anchor=self.use_five_anchor)

    tw.logger.info(f'Totally loading {len(self.targets)} samples.')

  def __len__(self):
    return len(self.targets)

  def __getitem__(self, idx):
    img_path, bbox_data = self.targets[idx]
    x1 = bbox_data['left']
    x2 = bbox_data['right']
    y1 = bbox_data['top']
    y2 = bbox_data['bottom']

    # load image
    origin = imread(img_path)[:, :, :3]
    h, w = origin.shape[:2]
    valid = True

    # detect face
    if self.detector == 'FAN':
      # bbox_fan = np.array([[x1, y1, x2, y2]])
      image = mesh.warp_face(origin, x1, y1, x2, y2, scale=1.6, crop_size=224)
      landmarks = self.det.get_landmarks(image)
      # just pick up first face
      if not landmarks:
        valid = False
      else:
        landmark = landmarks[0]

    elif self.detector == 'MTCNN':
      image = mesh.warp_face(origin, x1, y1, x2, y2, scale=1.6, crop_size=224)
      landmark = self.det.detect_faces(image)
      if not landmark:
        valid = False
      else:
        landmark = landmark[0]['keypoints']
        landmark = [*landmark.values()]
        landmark = np.array([list(i) for i in landmark])

    elif self.detector == 'BVT':
      image = mesh.warp_face(origin, x1, y1, x2, y2, scale=1.6, crop_size=224)
      landmark = self.det.get_face(image, det_interval=1, run_mode=0, run_level="platinum")
      if len(landmark) == 0:
        valid = False
      else:
        landmark = np.array(landmark[0].advancedLandmark)
        landmark = mesh.landmark_240_to_106(landmark)
        contour_idx = self.lm_map['frontal_contour']  # a list
        inner_idx = self.lm_map['frontal_inner']  # a list
        landmark = np.array(landmark[contour_idx + inner_idx])

    else:
      raise NotImplementedError(self.detector)

    # align image and landmark to standard 3d face points
    if len(landmark) > 0:
      image, landmark, _ = mesh.align_image(image, np.array(landmark), self.ldmk3d, use_five_anchor=self.use_five_anchor) # nopep8
    else:
      tw.logger.warn('failed to detect landmark for %s' % img_path)

    return self.transform({
        'image': image,
        'landmark': landmark,
        'bvt_pose': None,
        'msra_pose': None,
        'skin_mask': None,
        'parse_mask': None,
        'vertices_idx': None,
        'visibility': True,
        'ldmk_weight': None,
        'original': origin,
        'valid': valid,
        'path': img_path,
    })


class BigoFaceMesh(torch.utils.data.Dataset):

  """Bigo FaceMesh dataset with two kind of mode:

    - based on 2PCA (BFM)
    - based on bilinear

  """

  def __init__(self, path, transform, **kwargs):
    self.targets = []
    self.transform = transform
    self.src_image_size = 224
    self.render_image_size = 224
    self.model_image_size = 224

    if isinstance(path, str):
      path = [path, ]
    assert isinstance(path, (tuple, list))

    for file in path:
      with open(file, 'r') as rf:
        for line in rf.readlines():
          self.targets.append(line.strip())

    tw.logger.info(f'Totally loading {len(self.targets)} samples.')

  def __len__(self):
    return len(self.targets)

  def parse(self, content,
            use_visibility=False,
            use_random_noise=True,
            src_image_size=224,
            render_image_size=224,
            model_image_size=224):

    out = {}
    image = content['image'].reshape(src_image_size, src_image_size, 3)
    mask = content['skin_mask'].reshape(src_image_size, src_image_size)
    parse_mask = content['parse_mask'].reshape(src_image_size, src_image_size, 3)

    landmark = content['landmark'].astype('float32').reshape(68, 2)
    ldmk_weight = content['ldmk_weight'].astype('float32')

    # Add random crop
    random_thrs = 0.3  # percentage of random noise
    if use_random_noise and np.random.uniform() < random_thrs:
      offset_h = abs(int(np.random.normal(0, 10)))
      offset_w = abs(int(np.random.normal(0, 10)))
      target_h = src_image_size - 2 * offset_h
      target_w = src_image_size - 2 * offset_w

      image = image[offset_h: target_h + offset_h, offset_w: target_w + offset_w, :]
      mask = mask[offset_h: target_h + offset_h, offset_w: target_w + offset_w]

      image = cv2.resize(image, (src_image_size, src_image_size))
      mask = cv2.resize(mask, (src_image_size, src_image_size))

      scale = np.array([[src_image_size / target_w, src_image_size / target_h]])
      landmark = (landmark - np.array([[offset_w, offset_h]])) * scale

    # setting render size
    if render_image_size == src_image_size:
      render_image = image
    else:
      render_image = cv2.resize(image, (render_image_size, render_image_size))
      mask = cv2.resize(mask, (render_image_size, render_image_size))
      parse_mask = cv2.resize(parse_mask, (render_image_size, render_image_size))
      landmark = landmark / src_image_size * render_image_size

    # setting model input size
    # if model_image_size == src_image_size:
    #   model_image = image
    # else:
    #   model_image = cv2.resize(image, (model_image_size, model_image_size))

    pose = content['msra_pose'].astype('float32')
    vertices_idx = content['vertices_idx'].astype('int32')

    if use_visibility:
      visibility = content["visibility"].astype('float32')

    height = render_image_size  # hwc
    landmark[..., 1] = height - 1 - landmark[..., 1]
    M = mesh.estimate_norm(landmark, height).astype(np.float32)

    out['image'] = image
    out['skin_mask'] = mask
    out['parse_mask'] = parse_mask
    out['msra_pose'] = pose
    out['vertices_idx'] = vertices_idx
    out['landmark'] = landmark
    out['ldmk_weight'] = ldmk_weight
    out['bvt_pose'] = M
    out['render_image'] = render_image
    out['visibility'] = visibility

    return out

  def __getitem__(self, idx):
    """bigo facemesh dataset:

      Input: 
        a pickle file path

      Output: 
        image:         numpy.ndarray (224, 224, 3)
        landmark:      numpy.ndarray (68, 2)
        ldmk_weight:   numpy.ndarray (68,)
        skin_mask:     numpy.ndarray (224, 224)
        parse_mask:    numpy.ndarray (224, 224, 3)
        msra_pose:     numpy.ndarray (3,)
        bvt_pose:      numpy.ndarray (3,)
        trans_params:  numpy.ndarray (5,)
        vertices_idx:  numpy.ndarray (68,)
        visibility:    numpy.ndarray (68,)

    """
    path = self.targets[idx]
    with open(path, 'rb') as file:
      data = pickle.load(file)
    content = {}

    content['image'] = data['image'] if 'image' in data else None
    content['landmark'] = (data['landmark'] if 'landmark' in data else None)
    content['ldmk_weight'] = (data['ldmk_weight'] if 'ldmk_weight' in data else None)
    content['skin_mask'] = (data['skin_mask'] if 'skin_mask' in data else None)
    content['parse_mask'] = (data['parse_mask'] if 'parse_mask' in data else None)
    content['msra_pose'] = (data['msra_pose'] if 'msra_pose' in data else None)
    content['bvt_pose'] = (data['bvt_pose'] if 'bvt_pose' in data else None)
    content['trans_params'] = (data['trans_params'] if 'trans_params' in data else None)
    content['vertices_idx'] = (data['vertices_idx'] if 'vertices_idx' in data else None)
    content['visibility'] = (data['visibility'] if 'visibility' in data else None)

    parsed = self.parse(content=content,
                        use_visibility=True,
                        use_random_noise=False,
                        src_image_size=self.src_image_size,
                        render_image_size=self.render_image_size,
                        model_image_size=self.model_image_size)

    return self.transform({
        'image': parsed['image'],
        'landmark': np.array(parsed['landmark']).astype('float32'),
        'bvt_pose': np.array(parsed['bvt_pose']).astype('float32'),
        'msra_pose': np.array(parsed['msra_pose']).astype('float32'),
        'skin_mask': parsed['skin_mask'],
        'parse_mask': parsed['parse_mask'],
        'vertices_idx': parsed['vertices_idx'].astype('int32'),
        'visibility': parsed['visibility'],
        'ldmk_weight': np.array(parsed['ldmk_weight']).astype('float32'),
        'path': path,
    })

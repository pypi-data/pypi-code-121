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
"""AFFINE TRANSFORM

"""
from typing import Sequence
import math
import random
import cv2
import numpy as np
import torch
import torchvision.transforms.functional as tvf
import torchvision.transforms as tvt
import kornia
import PIL

from tw import transform as T
from tw import logger


#!<----------------------------------------------------------------------------
#!< VFLIP
#!<----------------------------------------------------------------------------

def _vflip_np(inputs):
  return np.ascontiguousarray(inputs[::-1, ...])


@T.MetaWrapper(support=[T.ImageMeta, T.VideoMeta, T.BoxListMeta, T.KpsListMeta])
def _vflip_meta(metas: Sequence[T.MetaBase], **kwargs):

  for meta in metas:

    if isinstance(meta, T.ImageMeta):
      meta.bin = np.ascontiguousarray(meta.bin[::-1, ...])

      if meta.source == T.COLORSPACE.FLOW:
        meta.bin = meta.bin * [1, -1]

    if isinstance(meta, T.VideoMeta):
      meta.bin = np.ascontiguousarray(meta.bin[:, ::-1, ...])

    if isinstance(meta, T.BoxListMeta):
      assert meta.is_affine_size
      x1, y1 = meta.bboxes[..., 0], meta.bboxes[..., 1]
      x2, y2 = meta.bboxes[..., 2], meta.bboxes[..., 3]
      meta.bboxes = np.stack([x1, meta.max_y - y2, x2, meta.max_y - y1], axis=1)

    if isinstance(meta, T.KpsListMeta):
      assert meta.is_affine_size
      x, y = meta.keypoints[..., 0], meta.keypoints[..., 1]
      meta.keypoints = np.stack([x, meta.max_y - y], axis=1)

  return metas


def vflip(inputs, **kwargs):
  if T.IsNumpy(inputs):
    return _vflip_np(inputs)
  elif T.IsMeta(inputs):
    return _vflip_meta(inputs, **kwargs)
  elif T.IsTensor(inputs):
    if inputs.ndim == 4:
      return torch.flip(inputs, dims=(2, ))
    elif inputs.ndim == 3:
      return torch.flip(inputs, dims=(1, ))
    else:
      raise NotImplementedError(inputs.ndim)
  elif T.IsPilImage(inputs):
    return tvt.functional.vflip(inputs)

#!<----------------------------------------------------------------------------
#!< HFLIP
#!<----------------------------------------------------------------------------


def _hflip_np(inputs):
  return np.ascontiguousarray(inputs[:, ::-1, ...])


@T.MetaWrapper(support=[T.ImageMeta, T.BoxListMeta, T.VideoMeta, T.KpsListMeta])
def _hflip_meta(metas: Sequence[T.MetaBase], **kwargs):

  for meta in metas:

    if isinstance(meta, T.ImageMeta):
      meta.bin = np.ascontiguousarray(meta.bin[:, ::-1, ...])

      if meta.source == T.COLORSPACE.FLOW:
        meta.bin = meta.bin * [-1, 1]

    if isinstance(meta, T.BoxListMeta):
      assert meta.is_affine_size
      x1, y1 = meta.bboxes[..., 0], meta.bboxes[..., 1]
      x2, y2 = meta.bboxes[..., 2], meta.bboxes[..., 3]
      meta.bboxes = np.stack([meta.max_x - x2, y1, meta.max_x - x1, y2], axis=1)

    if isinstance(meta, T.VideoMeta):
      meta.bin = np.ascontiguousarray(meta.bin[:, :, ::-1, ...])

    if isinstance(meta, T.KpsListMeta):
      assert meta.is_affine_size
      x, y = meta.keypoints[..., 0], meta.keypoints[..., 1]
      meta.keypoints = np.stack([meta.max_x - x, y], axis=1)

  return metas


def hflip(inputs, **kwargs):
  if T.IsNumpy(inputs):
    return _hflip_np(inputs)
  elif T.IsMeta(inputs):
    return _hflip_meta(inputs, **kwargs)
  elif T.IsTensor(inputs):
    if inputs.ndim == 4:
      return torch.flip(inputs, dims=(3, ))
    elif inputs.ndim == 3:
      return torch.flip(inputs, dims=(2, ))
    else:
      raise NotImplementedError(inputs.ndim)
  elif T.IsPilImage(inputs):
    return tvt.functional.hflip(inputs)

#!<----------------------------------------------------------------------------
#!< RANDOM FLIP
#!<----------------------------------------------------------------------------


def random_vflip(inputs, p=0.5, **kwargs):
  """random vertical flip sample.

  Args:
    p (float): the possibility to flip

  """
  if random.random() > p:
    return vflip(inputs, **kwargs)
  return inputs


def random_hflip(inputs, p=0.5, **kwargs):
  """random horizontal flip sample.

  Args:
    p (float): the possibility to flip

  """
  if random.random() > p:
    return hflip(inputs)
  return inputs


#!<----------------------------------------------------------------------------
#!< ROTATE
#!<----------------------------------------------------------------------------


def _rotate_numpy(inputs, angle, interpolation=cv2.INTER_LINEAR, border_mode=cv2.BORDER_CONSTANT, border_value=0):
  scale = 1.0
  shift = (0, 0)
  height, width = inputs.shape[:2]
  matrix = cv2.getRotationMatrix2D((width / 2, height / 2), angle, scale)
  matrix[0, 2] += shift[0]
  matrix[1, 2] += shift[1]
  cv2.warpAffine(inputs,
                 M=matrix,
                 dsize=(width, height),
                 dst=inputs,
                 flags=interpolation,
                 borderMode=border_mode,
                 borderValue=border_value)
  return inputs


@T.MetaWrapper(support=[T.ImageMeta, T.BoxListMeta, T.KpsListMeta])
def _rotate_meta(metas: Sequence[T.MetaBase], angle, interpolation=cv2.INTER_LINEAR,
                 border_mode=cv2.BORDER_CONSTANT, border_value=0, **kwargs):

  scale = 1.0
  shift = (0, 0)

  # params checking
  assert len(shift) == 2

  for meta in metas:
    if meta.source == T.COLORSPACE.HEATMAP:
      interpolation = cv2.INTER_NEAREST

    if isinstance(meta, T.ImageMeta):
      height, width = meta.bin.shape[:2]
      matrix = cv2.getRotationMatrix2D((width / 2, height / 2), angle, scale)
      matrix[0, 2] += shift[0]
      matrix[1, 2] += shift[1]
      cv2.warpAffine(meta.bin,
                     M=matrix,
                     dsize=(width, height),
                     dst=meta.bin,
                     flags=interpolation,
                     borderMode=border_mode,
                     borderValue=border_value)

    if isinstance(meta, T.BoxListMeta):
      width, height = meta.max_x, meta.max_y
      center = (width / 2, height / 2)
      matrix = cv2.getRotationMatrix2D(center, angle, scale)
      matrix[0, 2] += shift[0]
      matrix[1, 2] += shift[1]

      bbox = np.stack([meta.bboxes[:, 0], meta.bboxes[:, 1],
                       meta.bboxes[:, 2], meta.bboxes[:, 1],
                       meta.bboxes[:, 0], meta.bboxes[:, 3],
                       meta.bboxes[:, 2], meta.bboxes[:, 3]], axis=1).reshape(-1, 2)
      bbox = cv2.transform(bbox[None], matrix).squeeze().reshape(-1, 8)
      meta.bboxes = np.stack([
          np.amin(bbox[..., ::2], axis=1),
          np.amin(bbox[..., 1::2], axis=1),
          np.amax(bbox[..., ::2], axis=1),
          np.amax(bbox[..., 1::2], axis=1),
      ], axis=1)

      if meta.visibility:
        meta.clip_with_affine_size()

    if isinstance(meta, T.KpsListMeta):
      width, height = meta.max_x, meta.max_y
      center = (width / 2, height / 2)
      matrix = cv2.getRotationMatrix2D(center, angle, scale)
      matrix[0, 2] += shift[0]  # * width
      matrix[1, 2] += shift[1]  # * height
      meta.keypoints = cv2.transform(meta.keypoints[None], matrix).squeeze()
      if meta.visibility:
        meta.clip_with_affine_size()

  return metas


def rotate(inputs, angle, interpolation=cv2.INTER_LINEAR, border_mode=cv2.BORDER_CONSTANT, border_value=0, **kwargs):
  """rotate

  Args:
      inputs ([type]): [description]
      angle (float): degree representation
      interpolation ([type], optional): [description]. Defaults to cv2.INTER_LINEAR.
      border_mode ([type], optional): [description]. Defaults to cv2.BORDER_CONSTANT.
      border_value (int, optional): [description]. Defaults to 0.

  Raises:
      NotImplementedError: [description]
      NotImplementedError: [description]
      NotImplementedError: [description]

  Returns:
      [type]: [description]
  """
  if T.IsNumpy(inputs):
    return _rotate_numpy(inputs, angle, interpolation, border_mode, border_value)
  elif T.IsMeta(inputs):
    return _rotate_meta(inputs, angle, interpolation, border_mode, border_value, **kwargs)
  elif T.IsTensor(inputs):
    assert border_value == 0
    assert inputs.ndim == 4
    return kornia.rotate(inputs, torch.tensor(angle).to(inputs.device), mode=T.INTER_CV_TO_TCH[interpolation])
  elif T.IsPilImage(inputs):
    raise NotImplementedError


def random_rotate(inputs, angle_limit=(-30, 30), interpolation=cv2.INTER_LINEAR,
                  border_mode=cv2.BORDER_CONSTANT, border_value=0, **kwargs):
  """rotate

  Args:
      inputs ([type]): [description]
      angle (float): degree representation
      interpolation ([type], optional): [description]. Defaults to cv2.INTER_LINEAR.
      border_mode ([type], optional): [description]. Defaults to cv2.BORDER_CONSTANT.
      border_value (int, optional): [description]. Defaults to 0.

  Raises:
      NotImplementedError: [description]
      NotImplementedError: [description]
      NotImplementedError: [description]

  Returns:
      [type]: [description]
  """

  angle = random.uniform(angle_limit[0], angle_limit[1])

  if T.IsNumpy(inputs):
    raise NotImplementedError
  elif T.IsMeta(inputs):
    return _rotate_meta(inputs, angle, interpolation, border_mode, border_value, **kwargs)
  elif T.IsTensor(inputs):
    raise NotImplementedError
  elif T.IsPilImage(inputs):
    raise NotImplementedError

#!<----------------------------------------------------------------------------
#!< Multiple Rigid Transformation
#!<----------------------------------------------------------------------------


def _restoration_augment_np(img, mode):
  if mode == 0:
    return img
  elif mode == 1:
    return np.flipud(np.rot90(img))
  elif mode == 2:
    return np.flipud(img)
  elif mode == 3:
    return np.rot90(img, k=3)
  elif mode == 4:
    return np.flipud(np.rot90(img, k=2))
  elif mode == 5:
    return np.rot90(img)
  elif mode == 6:
    return np.rot90(img, k=2)
  elif mode == 7:
    return np.flipud(np.rot90(img, k=3))


@T.MetaWrapper(support=[T.ImageMeta, ])
def _restoration_augment_meta(metas, mode):
  for meta in metas:
    if isinstance(meta, T.ImageMeta):
      meta.bin = _restoration_augment_np(meta.bin, mode)
  return metas


def _restoration_augment_tensor(img, mode):
  if mode == 0:
    return img
  elif mode == 1:
    return img.rot90(1, [2, 3]).flip([2])
  elif mode == 2:
    return img.flip([2])
  elif mode == 3:
    return img.rot90(3, [2, 3])
  elif mode == 4:
    return img.rot90(2, [2, 3]).flip([2])
  elif mode == 5:
    return img.rot90(1, [2, 3])
  elif mode == 6:
    return img.rot90(2, [2, 3])
  elif mode == 7:
    return img.rot90(3, [2, 3]).flip([2])


def restoration_augment(inputs, mode, **kwargs):
  """super resolution augmentation

    Ref: Kai Zhang (github: https://github.com/cszn)

  Args:
      inputs (_type_): _description_
      mode (_type_): _description_

  Returns:
      _type_: _description_
  """
  if T.IsNumpy(inputs):
    return _restoration_augment_np(inputs, mode)
  elif T.IsMeta(inputs):
    return _restoration_augment_meta(inputs, mode)
  elif T.IsTensor(inputs):
    return _restoration_augment_tensor(inputs, mode)
  elif T.IsPilImage(inputs):
    raise NotImplementedError


#!<----------------------------------------------------------------------------
#!< RANDOM GAMMA
#!<----------------------------------------------------------------------------

def _apply_affine_np(img, theta=None, t_x=0, t_y=0, zoom=1.0, shear=1.0, phi=0.0, interpolation=cv2.INTER_LINEAR):

  h, w = img.shape[:2]

  if theta is None:
    theta = _generate_affine_theta(t_x, t_y, zoom, shear, phi)

  # T is similar transform matrix
  T = np.array([[1. / (w - 1.), 0., -0.5], [0., 1. / (h - 1.), -0.5],
                [0., 0., 1.]], np.float32)

  T_inv = np.linalg.inv(T)

  # theta is affine transformations in world coordinates, with origin at top
  # left corner of pictures and picture's width range and height range
  # from [0, width] and [0, height].
  theta_world = T_inv @ theta @ T

  return cv2.warpAffine(img, theta_world[:2, :], (w, h), flags=interpolation)


def _apply_affine_flow_np(flow, theta=None, t_x=0, t_y=0, zoom=1.0, shear=1.0, phi=0.0, interpolation=cv2.INTER_LINEAR):

  h, w = flow.shape[:2]

  if theta is None:
    theta = _generate_affine_theta(t_x, t_y, zoom, shear, phi)

  # T is similar transform matrix
  T = np.array([[1. / (w - 1.), 0., -0.5], [0., 1. / (h - 1.), -0.5],
                [0., 0., 1.]], np.float32)

  T_inv = np.linalg.inv(T)

  # theta is affine transformations in world coordinates, with origin at top
  # left corner of pictures and picture's width range and height range
  # from [0, width] and [0, height].
  theta_world = T_inv @ theta @ T

  flow = cv2.warpAffine(flow, theta_world[:2, :], (w, h), flags=interpolation)

  """
  X1                 Affine(theta1)             X1'
              x                                   x
  theta1(-1) y           ->                      y
              1                                   1

  X2                 Affine(theta2)             X2'
              x   u                                         x   u
  theta1(-1) y + v       ->           theta2 x {theta1(-1) y + v}
              1   0                                         1   0
                                      flow' = X2' -X1'
  """

  # (u, v) -> (u, v, 0); shape (height, width, 2) -> (height, width, 3)
  homo_flow = np.concatenate((flow, np.zeros((height, width, 1))), axis=2)

  xx, yy = np.meshgrid(range(width), range(height))

  # grid of homogeneous coordinates
  homo_grid = np.stack((xx, yy, np.ones((height, width))), axis=2).astype(flow.dtype)

  # theta2 x [u, v, 0]T + (theta2 x theta1(-1) - [1, 1, 1]) x [x, y, 1]T
  flow_final = homo_grid @ (theta2 @ np.linalg.inv(theta1) - np.eye(3)).T + homo_flow @ theta2.T

  return flow_final[:, :, :2]


@T.MetaWrapper(support=[T.ImageMeta])
def _apply_affine_meta(metas: Sequence[T.MetaBase], theta=None, t_x=0, t_y=0, zoom=1.0, shear=1.0, phi=0.0):

  if theta is None:
    theta = _generate_affine_theta(t_x, t_y, zoom, shear, phi)

  for meta in metas:

    if meta.source in [T.COLORSPACE.HEATMAP]:
      interpolation = cv2.INTER_NEAREST
    else:
      interpolation = cv2.INTER_LINEAR

    if isinstance(meta, T.ImageMeta):
      meta.bin = _apply_affine_np(meta.bin, theta=theta, interpolation=interpolation)

  return metas


def _generate_affine_theta(t_x, t_y, zoom, shear, phi):
  """generate a affine matrix

  Args:
      t_x (float):
      t_y (float):
      zoom (float):
      shear (float):
      phi (float): unit in rad

  Returns:
      theta: _description_
  """
  sin_phi = np.sin(phi)
  cos_phi = np.cos(phi)

  translate_mat = np.array([
      [1., 0., t_x],
      [0., 1., t_y],
      [0., 0., 1.],
  ])

  rotate_mat = np.array([
      [cos_phi, -sin_phi, 0.],
      [sin_phi, cos_phi, 0.],
      [0., 0., 1.],
  ])

  shear_mat = np.array([
      [shear, 0., 0.],
      [0., 1. / shear, 0.],
      [0., 0., 1.],
  ])

  zoom_mat = np.array([
      [zoom, 0., 0.],
      [0., zoom, 0.],
      [0., 0., 1.],
  ])

  T = translate_mat @ rotate_mat @ shear_mat @ zoom_mat
  return T


def _generate_random_affine_theta(translates, zoom, shear, rotate, preserve_valid):
  """A valid affine transform is an affine transform which guarantees the
    transformed image covers the whole original picture frame.
  """
  def is_valid(theta):
    bounds = np.array([
        [-0.5, -0.5, 1.],  # left top
        [-0.5, 0.5, 1.],  # left bottom
        [0.5, -0.5, 1.],  # right top
        [0.5, 0.5, 1.],  # right bottom
    ])
    """
    (-0.5, -0.5)          (0.5, -0.5)
                 --------
                |        |
                |        |
                |        |
                 --------
    (-0.5, 0.5)          (0.5, 0.5)
    """
    bounds = (np.linalg.inv(theta) @ bounds.T).T

    valid = ((bounds[:, :2] >= -0.5) & (bounds[:, :2] <= 0.5)).all()
    return valid

  valid = False
  theta = np.identity(3)

  while not valid:
    zoom_ = np.random.uniform(zoom[0], zoom[1])
    shear_ = np.random.uniform(shear[0], shear[1])
    t_x = np.random.uniform(-translates[0], translates[0])
    t_y = np.random.uniform(-translates[1], translates[1])
    phi = np.random.uniform(rotate[0] * np.pi / 180., rotate[1] * np.pi / 180.)
    T = _generate_affine_theta(t_x, t_y, zoom_, shear_, phi)
    theta_propose = T @ theta
    if not preserve_valid:
      break
    valid = is_valid(theta_propose)

  return theta_propose


def random_affine(inputs, translates=(0.05, 0.05), zoom=(1.0, 1.5),
                  shear=(0.86, 1.16), rotate=(-10., 10.), preserve_valid=True, **kwargs):
  """Random affine transformation of images, flow map and occlusion map (if
    available).

    Keys of global_transform and relative_transform should be the subset of
    ('translates', 'zoom', 'shear', 'rotate'). And also, each key and its
    corresponding values has to satisfy the following rules:
        - translates: the translation ratios along x axis and y axis. Defaults
            to(0., 0.).
        - zoom: the min and max zoom ratios. Defaults to (1.0, 1.0).
        - shear: the min and max shear ratios. Defaults to (1.0, 1.0).
        - rotate: the min and max rotate degree. Defaults to (0., 0.).
  """
  theta_propose = _generate_random_affine_theta(
      translates, zoom, shear, rotate, preserve_valid)

  if T.IsNumpy(inputs):
    raise _apply_affine_np(inputs, theta=theta_propose)
  elif T.IsMeta(inputs):
    return _apply_affine_meta(inputs, theta=theta_propose, **kwargs)
  elif T.IsTensor(inputs):
    raise NotImplementedError
  elif T.IsPilImage(inputs):
    raise NotImplementedError
